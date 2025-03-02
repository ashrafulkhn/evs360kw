import logging


class Gun:
    # Class-level dictionaries to store all guns data
    soc_data = {f"Gun{i}": 0 for i in range(1, 7)}
    demand_data = {f"Gun{i}": 0 for i in range(1, 7)}
    status_data = {f"Gun{i}": 0 for i in range(1, 7)}

    def __init__(self, gun_number):
        self.gun_number = gun_number
        self.soc = 0
        self.demand = 0
        self.status = 0

    def update_data(self, message_type, value):
        if message_type == "soc":
            # Convert SOC to float
            try:
                float_value = float(value)
                if self.soc != float_value:
                    self.soc = float_value
                    Gun.soc_data[f"Gun{self.gun_number}"] = float_value
                    self.soc_changed(Gun.soc_data)
                    print("\nSOC Data for all guns:", Gun.soc_data)
            except ValueError:
                logging.error(f"Invalid SOC value: {value}")
        elif message_type == "demand":
            # Convert demand to float
            try:
                float_value = float(value)
                if self.demand != float_value:
                    self.demand = float_value
                    Gun.demand_data[f"Gun{self.gun_number}"] = float_value
                    self.demand_changed(Gun.demand_data)
                    print("\nDemand Data for all guns:", Gun.demand_data)
            except ValueError:
                logging.error(f"Invalid demand value: {value}")
        elif message_type == "vehicle_status":
            try:
                # Try to convert status to integer
                int_value = int(value)
                if self.status != int_value:
                    self.status = int_value
                    Gun.status_data[f"Gun{self.gun_number}"] = int_value
                    self.status_changed(Gun.status_data)
                    print("\nStatus Data for all guns:", Gun.status_data)
            except ValueError:
                logging.error(f"Invalid vehicle_status value: {value}")

    def soc_changed(self, value):
        logging.info(f"Gun {self.gun_number} SOC changed to: {value}")

    def demand_changed(self, value):
        logging.info(f"Gun {self.gun_number} Demand changed to: {value}")
        
        # Process the demand change through the demand processor
        try:
            from demand_processor import DemandProcessor
            from config_manager import ConfigManager
            from contactor_controller import ContactorController
            
            # Create config manager for logging
            if not hasattr(Gun, '_config_manager'):
                Gun._config_manager = ConfigManager()
            
            # Singleton pattern - create or get existing processor
            if not hasattr(Gun, '_demand_processor'):
                Gun._demand_processor = DemandProcessor()
            
            # Get or create contactor controller
            if not hasattr(Gun, '_contactor_controller'):
                Gun._contactor_controller = ContactorController()
            
            # We now get a float directly since we convert in update_data
            demand_value = self.demand
            
            # Get max allowed power for this gun
            max_power = Gun._config_manager.get_gun_max_power(self.gun_number)
            if demand_value > max_power:
                logging.warning(f"Gun {self.gun_number} demand of {demand_value}kW exceeds max allowed {max_power}kW")
            
            # Process the demand change
            Gun._demand_processor.process_demand_change(self.gun_number, demand_value)
            
            # Get allocation information after processing
            allocation = Gun._demand_processor.get_gun_power_allocation(self.gun_number)
            logging.info(f"Gun {self.gun_number} power allocation: {allocation}")
            
            # Display allocation for all guns when demand changes
            self.display_all_gun_allocations()
            
        except Exception as e:
            logging.error(f"Error processing demand change: {str(e)}")
            
    def display_all_gun_allocations(self):
        """Display active guns with their power modules and closed contactors"""
        try:
            demand_processor = Gun._demand_processor
            contactor_controller = Gun._contactor_controller
            
            # Display header
            logging.info("=== CURRENT GUN ALLOCATIONS ===")
            
            # For each gun, display its allocation if active
            for gun_id in range(1, 7):
                # Get assigned modules from demand processor
                allocation = demand_processor.get_gun_power_allocation(gun_id)
                if 'modules_assigned' in allocation and allocation['modules_assigned']:
                    # Get connected modules from contactor controller
                    connected_modules = contactor_controller.get_connected_modules(gun_id)
                    
                    logging.info(f"Gun {gun_id}:")
                    logging.info(f"  - Demand: {allocation.get('demand', 0)} kW")
                    logging.info(f"  - Assigned modules: {allocation.get('modules_assigned', [])}")
                    logging.info(f"  - Connected via contactors: {connected_modules}")
                    logging.info(f"  - Total capacity: {allocation.get('total_capacity_kw', 0)} kW")
        except Exception as e:
            logging.error(f"Error displaying gun allocations: {str(e)}")

    def status_changed(self, value):
        logging.info(f"Gun {self.gun_number} Status changed to: {value}")
