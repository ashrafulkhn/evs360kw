
import logging


class Gun:
    # Class-level dictionaries to store all guns data
    soc_data = {f"Gun{i}": None for i in range(1, 7)}
    demand_data = {f"Gun{i}": None for i in range(1, 7)}
    status_data = {f"Gun{i}": None for i in range(1, 7)}

    def __init__(self, gun_number):
        self.gun_number = gun_number
        self.soc = None
        self.demand = None
        self.status = None

    def update_data(self, message_type, value):
        if message_type == "soc":
            if self.soc != value:
                self.soc = value
                Gun.soc_data[f"Gun{self.gun_number}"] = value
                self.soc_changed(value)
                print("\nSOC Data for all guns:", Gun.soc_data)
        elif message_type == "demand":
            if self.demand != value:
                self.demand = value
                Gun.demand_data[f"Gun{self.gun_number}"] = value
                self.demand_changed(value)
                print("\nDemand Data for all guns:", Gun.demand_data)
        elif message_type == "vehicle_status":
            if self.status != value:
                self.status = value
                Gun.status_data[f"Gun{self.gun_number}"] = value
                self.status_changed(value)
                print("\nStatus Data for all guns:", Gun.status_data)

    def soc_changed(self, value):
        logging.info(f"Gun {self.gun_number} SOC changed to: {value}")

    def demand_changed(self, value):
        logging.info(f"Gun {self.gun_number} Demand changed to: {value}")

    def status_changed(self, value):
        logging.info(f"Gun {self.gun_number} Status changed to: {value}")
