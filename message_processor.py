
import logging

class MessageProcessor:
    def process_message(self, topic_name: str, payload: str):
        try:
            client_id = topic_name.split('/')[1]
            if client_id == 'D1':
                self.handle_d1_message(topic_name, payload)
            elif client_id == 'D2':
                self.handle_d2_message(topic_name, payload)
            elif client_id == 'D3':
                self.handle_d3_message(topic_name, payload)
        except Exception as e:
            logging.error(f"Error processing message for {topic_name}: {str(e)}")
    
    def handle_d1_message(self, topic: str, payload: str):
        logging.info(f"Processing D1 message from {topic}: {payload}")
        # Add specific D1 handling logic here
    
    def handle_d2_message(self, topic: str, payload: str):
        logging.info(f"Processing D2 message from {topic}: {payload}")
        # Add specific D2 handling logic here
    
    def handle_d3_message(self, topic: str, payload: str):
        logging.info(f"Processing D3 message from {topic}: {payload}")
        # Add specific D3 handling logic here
