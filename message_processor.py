
import logging
from gun import Gun

class MessageProcessor:
    def __init__(self):
        # Initialize 6 guns
        self.guns = {i: Gun(i) for i in range(1, 7)}
        
        # Map device and topic gun_id to actual gun numbers
        self.gun_mapping = {
            'D1': {1: 1, 2: 2},  # D1's gun_ids 1,2 map to Gun1,Gun2
            'D2': {1: 3, 2: 4},  # D2's gun_ids 1,2 map to Gun3,Gun4
            'D3': {1: 5, 2: 6}   # D3's gun_ids 1,2 map to Gun5,Gun6
        }

    def process_message(self, topic: str, payload: str):
        try:
            # Parse topic: vesec/gun_id/message_type/device
            parts = topic.split('/')
            topic_gun_id = int(parts[1])
            message_type = parts[2]
            device = parts[3]

            if device in self.gun_mapping:
                # Map to actual gun number
                actual_gun_number = self.gun_mapping[device][topic_gun_id]
                gun = self.guns[actual_gun_number]
                gun.update_data(message_type, payload)
                
                logging.info(f"Updated Gun{actual_gun_number} from {device} with {message_type}: {payload}")
        except Exception as e:
            logging.error(f"Error processing message for {topic}: {str(e)}")

    def get_gun_data(self, gun_number):
        if gun_number in self.guns:
            gun = self.guns[gun_number]
            return {
                'soc': gun.soc,
                'demand': gun.demand,
                'status': gun.status
            }
        return None
