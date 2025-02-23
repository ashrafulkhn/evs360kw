import logging


class Gun:

    def __init__(self, gun_number):
        self.gun_number = gun_number
        self.soc = None
        self.demand = None
        self.status = None

    def update_data(self, message_type, value):
        if message_type == "soc":
            if self.soc != value:
                self.soc = value
                self.soc_changed(value)
        elif message_type == "demand":
            if self.demand != value:
                self.demand = value
                self.demand_changed(value)
        elif message_type == "vehicle_status":
            if self.status != value:
                self.status = value
                self.status_changed(value)

    def soc_changed(self, value):
        logging.info(f"Gun {self.gun_number} SOC changed to: {value}")

    def demand_changed(self, value):
        logging.info(f"Gun {self.gun_number} Demand changed to: {value}")

    def status_changed(self, value):
        logging.info(f"Gun {self.gun_number} Status changed to: {value}")
