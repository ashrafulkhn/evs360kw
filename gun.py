import logging


class Gun:
    soc_data = {}
    demand_data = {}
    status_data = {}

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
                print(f"\nSOC Data Dictionary: {Gun.soc_data}")
        elif message_type == "demand":
            if self.demand != value:
                self.demand = value
                Gun.demand_data[f"Gun{self.gun_number}"] = value
                self.demand_changed(value)
                print(f"\nDemand Data Dictionary: {Gun.demand_data}")
        elif message_type == "vehicle_status":
            if self.status != value:
                self.status = value
                Gun.status_data[f"Gun{self.gun_number}"] = value
                self.status_changed(value)
                print(f"\nStatus Data Dictionary: {Gun.status_data}")

    def soc_changed(self, value):
        logging.info(f"Gun {self.gun_number} SOC changed to: {value}")

    def demand_changed(self, value):
        logging.info(f"Gun {self.gun_number} Demand changed to: {value}")

    def status_changed(self, value):
        logging.info(f"Gun {self.gun_number} Status changed to: {value}")
