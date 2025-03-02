import logging
from typing import Dict, List
from power_module_controller import PowerModuleController
from contactor_controller import ContactorController
from config_manager import ConfigManager

class DemandProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.power_controller = PowerModuleController()
        self.contactor_controller = ContactorController()

        # Track demand per gun
        self.gun_demands = {i: 0.0 for i in range(1, 7)}

        # Track which modules are assigned to which guns
        self.gun_module_assignments: Dict[int, List[int]] = {i: [] for i in range(1, 7)}

    def process_demand_change(self, gun_id: int, demand: float):
        """
        Process a demand change for a specific gun

        Args:
            gun_id: The gun ID (1-6)
            demand: The new power demand in kW
        """
        self.logger.info(f"Processing demand change for Gun {gun_id}: {demand}kW")

        # Update the demand for this gun
        if 1 <= gun_id <= 6:
            self.gun_demands[gun_id] = demand
        else:
            self.logger.error(f"Invalid gun ID: {gun_id}")
            return

        # Recalculate module assignments for all guns
        self._reassign_modules()

    def _reassign_modules(self):
        """Reassign power modules to guns based on current demands and power limits"""
        # Sort guns by demand (highest first)
        sorted_guns = sorted(self.gun_demands.items(), key=lambda x: x[1], reverse=True)

        # Reset all assignments
        self.gun_module_assignments = {i: [] for i in range(1, 7)}

        # Track which modules are already assigned
        assigned_modules = set()

        # Assign modules to guns based on demand
        module_power = self.config.get_module_power_capacity()  # kW per module

        for gun_id, demand in sorted_guns:
            if demand <= 0:
                continue

            # Get the maximum power allowed for this gun from config
            max_allowed_power = self.config.get_gun_max_power(gun_id)

            # Limit demand to max allowed power
            capped_demand = min(demand, max_allowed_power)
            if capped_demand < demand:
                self.logger.warning(f"Gun {gun_id} demand of {demand}kW exceeds max allowed {max_allowed_power}kW, capping demand")

            # Calculate how many modules this gun needs
            modules_needed = min(9, max(1, int((capped_demand + module_power - 1) // module_power)))
            modules_assigned = 0

            # Assign available modules
            for module_id in range(1, 10):  # 9 modules total
                if module_id not in assigned_modules and modules_assigned < modules_needed:
                    self.gun_module_assignments[gun_id].append(module_id)
                    assigned_modules.add(module_id)
                    modules_assigned += 1

            # Get SOC data from Gun class for logging
            from gun import Gun
            soc_data = Gun.soc_data
            total_assigned = len(self.gun_module_assignments[gun_id])
            soc = soc_data.get(f"Gun{gun_id}", 0)
            self.logger.info(f"Assigned {total_assigned} modules to Gun {gun_id} (demand: {capped_demand}kW/{demand}kW requested, SOC: {soc}%)")


        # Identify guns with unmet demand after initial allocation
        demanding_guns = [(gun_id, demand) for gun_id, demand in sorted_guns if demand > 0 and not self.gun_module_assignments[gun_id]]

        # Get SOC data from Gun class for rebalancing
        from gun import Gun
        soc_data = Gun.soc_data

        # After all assignments, check if all demanding guns have at least one module
        for gun_id, demand in sorted_guns:
            if demand > 0 and not self.gun_module_assignments[gun_id]:
                self.logger.warning(f"Gun {gun_id} has demand but no modules assigned, attempting rebalance")

                # Find gun with most modules to borrow from, considering SOC
                potential_donors = []
                for g, mods in self.gun_module_assignments.items():
                    if len(mods) > 1:  # Only consider guns with >1 module
                        g_soc = soc_data.get(f"Gun{g}", 100)  # Get SOC for this gun
                        requesting_soc = soc_data.get(f"Gun{gun_id}", 0)

                        # Calculate score: Higher for donors with high SOC and many modules
                        # when requester has low SOC
                        soc_diff = g_soc - requesting_soc
                        if soc_diff > 20:  # Only borrow if donor SOC is at least 20% higher
                            score = len(mods) * soc_diff / 100
                            potential_donors.append((g, mods, score))

                # Sort by score (higher is better donor candidate)
                potential_donors.sort(key=lambda x: x[2], reverse=True)

                if potential_donors:
                    # Borrow from highest scoring donor
                    donor_gun, donor_modules, score = potential_donors[0]
                    borrowed_module = self.gun_module_assignments[donor_gun].pop()
                    self.gun_module_assignments[gun_id].append(borrowed_module)
                    self.logger.info(f"SOC-based rebalance: Borrowed module {borrowed_module} from Gun {donor_gun} (SOC: {soc_data.get(f'Gun{donor_gun}', 0)}%) for Gun {gun_id} (SOC: {soc_data.get(f'Gun{gun_id}', 0)}%)")
                else:
                    # Fallback to the original method if no SOC-appropriate donors
                    most_modules_gun = max(
                        [(g, len(mods)) for g, mods in self.gun_module_assignments.items() if mods],
                        key=lambda x: x[1],
                        default=(None, 0)
                    )

                    if most_modules_gun[0] is not None and most_modules_gun[1] > 1:
                        # Borrow one module from the gun with the most modules
                        donor_gun = most_modules_gun[0]
                        borrowed_module = self.gun_module_assignments[donor_gun].pop()
                        self.gun_module_assignments[gun_id].append(borrowed_module)
                        self.logger.info(f"Fallback rebalance: Borrowed module {borrowed_module} from Gun {donor_gun} for Gun {gun_id}")

        # Second pass: Distribute remaining modules based on demand ratio and SOC
        module_power = self.config.get_module_power_capacity()  # kW per module
        remaining_modules = [m for m in range(1, 10) if m not in assigned_modules]

        # Get SOC data for module allocation prioritization
        from gun import Gun
        soc_data = Gun.soc_data

        # If we have demanding guns and remaining modules
        if demanding_guns and remaining_modules:
            # Calculate total scoring factor (demand weighted by inverse SOC)
            gun_scores = []
            for gun_id, demand in demanding_guns:
                max_allowed_power = self.config.get_gun_max_power(gun_id)
                capped_demand = min(demand, max_allowed_power)

                # Get SOC for this gun (default to 100% if not found)
                soc = soc_data.get(f"Gun{gun_id}", 100)

                # Calculate score: higher demand and lower SOC = higher priority
                # Formula: demand * (100 - soc + 10) / 110 
                # This gives guns with lower SOC more priority while still considering demand
                # Adding 10 to prevent zero priority at 100% SOC
                soc_factor = (100 - soc + 10) / 110  # Results in ~1.0 at 0% SOC, ~0.09 at 100% SOC
                score = capped_demand * soc_factor

                gun_scores.append((gun_id, demand, capped_demand, soc, score))

            # Sort by score (highest priority first)
            gun_scores.sort(key=lambda x: x[4], reverse=True)

            # Calculate total score for proportional allocation
            total_score = sum(score for _, _, _, _, score in gun_scores)

            # Allocate remaining modules based on score ratio
            for gun_id, demand, capped_demand, soc, score in gun_scores:
                # Ideal module count based on score ratio
                if total_score > 0:
                    score_ratio = score / total_score
                    ideal_modules = max(1, min(9, round(score_ratio * (9 - len(demanding_guns)) + 1)))
                else:
                    ideal_modules = 1

                # Assign remaining modules
                modules_assigned = 0
                for module_id in remaining_modules:
                    if modules_assigned < ideal_modules:
                        self.gun_module_assignments[gun_id].append(module_id)
                        assigned_modules.add(module_id)
                        modules_assigned += 1
                        remaining_modules.remove(module_id)

        # Apply the assignments
        self._apply_assignments()

    def _apply_assignments(self):
        """Apply module assignments by activating modules and connecting contactors"""
        # First, determine which modules need to be active
        active_modules = set()
        for gun_id, module_ids in self.gun_module_assignments.items():
            active_modules.update(module_ids)

        # Activate/deactivate power modules as needed
        for module_id in range(1, 10):
            module = self.power_controller.modules[module_id - 1]  # 0-indexed list
            if module_id in active_modules and not module.is_active:
                module.start()
            elif module_id not in active_modules and module.is_active:
                module.stop()

        # Update contactor connections for each gun
        for gun_id, module_ids in self.gun_module_assignments.items():
            if module_ids:  # If this gun has assigned modules
                self.contactor_controller.connect_gun_to_modules(gun_id, module_ids)
            else:
                self.contactor_controller.disconnect_gun(gun_id)

    def get_gun_power_allocation(self, gun_id: int) -> Dict:
        """
        Get power allocation information for a specific gun

        Returns:
            Dict with demand, modules assigned, and total power capacity
        """
        if gun_id not in self.gun_demands:
            return {"error": "Invalid gun ID"}

        modules = self.gun_module_assignments.get(gun_id, [])
        module_power = self.config.get_module_power_capacity()
        total_capacity = len(modules) * module_power
        max_allowed = self.config.get_gun_max_power(gun_id)

        return {
            "gun_id": gun_id,
            "demand": self.gun_demands[gun_id],
            "max_allowed_kw": max_allowed,
            "modules_assigned": modules,
            "total_capacity_kw": total_capacity,
            "module_power_kw": module_power,
            "status": "active" if modules else "inactive"
        }