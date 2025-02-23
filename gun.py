
class Gun:
    def __init__(self, gun_number):
        self.gun_number = gun_number
        self.soc = None
        self.demand = None
        self.status = None

    def update_data(self, message_type, value):
        if message_type == "soc":
            self.soc = value
        elif message_type == "demand":
            self.demand = value
        elif message_type == "vehicle_status":
            self.status = value
