
import paho.mqtt.client as mqtt
import logging
from datetime import datetime
from message_processor import MessageProcessor

class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.topic_data = {}
        self.message_processor = MessageProcessor()
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            print("Connecting to MQTT broker...")
            result = self.client.connect("broker.hivemq.com", 1883, 60)
            if result == 0:
                print("Successfully connected to MQTT broker")
                logging.info("Connected to MQTT broker")
            else:
                print(f"Failed to connect to MQTT broker with result code {result}")
                logging.error(f"Failed to connect to MQTT broker with result code {result}")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {str(e)}")
            logging.error(f"Failed to connect to MQTT broker: {str(e)}")
            raise
    
    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected with result code {rc}")
        for d in ['D1', 'D2', 'D3']:
            for i in range(1, 11):
                topic = f"Topic{i}/{d}"
                self.client.subscribe(topic)
                logging.debug(f"Subscribed to {topic}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            self.set_topic_data(msg.topic, payload)
            logging.debug(f"Received message on {msg.topic}: {payload}")
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
    
    def set_topic_data(self, topic_name: str, payload: str):
        self.topic_data[topic_name] = {
            'value': payload,
            'timestamp': datetime.now().isoformat()
        }
        self.message_processor.process_message(topic_name, payload)
    
    def run(self):
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down MQTT client")
            self.client.disconnect()
        except Exception as e:
            logging.error(f"Error in MQTT loop: {str(e)}")
