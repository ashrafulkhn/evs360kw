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
            if self.soc != value:
                self.soc = value
                Gun.soc_data[f"Gun{self.gun_number}"] = value
                self.soc_changed(Gun.soc_data)
                print("\nSOC Data for all guns:", Gun.soc_data)
        elif message_type == "demand":
            if self.demand != value:
                self.demand = value
                Gun.demand_data[f"Gun{self.gun_number}"] = value
                self.demand_changed(Gun.demand_data)
                print("\nDemand Data for all guns:", Gun.demand_data)
        elif message_type == "vehicle_status":
            if self.status != value:
                self.status = value
                Gun.status_data[f"Gun{self.gun_number}"] = value
                self.status_changed(Gun.status_data)
                print("\nStatus Data for all guns:", Gun.status_data)

    def soc_changed(self, value):
        logging.info(f"Gun {self.gun_number} SOC changed to: {value}")

    def demand_changed(self, value):
        logging.info(f"Gun {self.gun_number} Demand changed to: {value}")
        
        # Process the demand change through the demand processor
        try:
            from demand_processor import DemandProcessor
            from config_manager import ConfigManager
            
            # Create config manager for logging
            if not hasattr(Gun, '_config_manager'):
                Gun._config_manager = ConfigManager()
            
            # Singleton pattern - create or get existing processor
            if not hasattr(Gun, '_demand_processor'):
                Gun._demand_processor = DemandProcessor()
            
            # Convert demand to float if it's a string
            if isinstance(value, str):
                try:
                    demand_value = float(value)
                except ValueError:
                    logging.error(f"Invalid demand value: {value}")
                    return
            else:
                demand_value = float(value)
            
            # Get max allowed power for this gun
            max_power = Gun._config_manager.get_gun_max_power(self.gun_number)
            if demand_value > max_power:
                logging.warning(f"Gun {self.gun_number} demand of {demand_value}kW exceeds max allowed {max_power}kW")
            
            # Process the demand change
            Gun._demand_processor.process_demand_change(self.gun_number, demand_value)
            
            # Get allocation information after processing
            allocation = Gun._demand_processor.get_gun_power_allocation(self.gun_number)
            logging.info(f"Gun {self.gun_number} power allocation: {allocation}")
            
        except Exception as e:
            logging.error(f"Error processing demand change: {str(e)}")

    def status_changed(self, value):
        logging.info(f"Gun {self.gun_number} Status changed to: {value}")
