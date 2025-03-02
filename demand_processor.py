
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
            
            self.logger.info(f"Assigned {modules_assigned} modules to Gun {gun_id} (demand: {capped_demand}kW/{demand}kW requested)")
        
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
