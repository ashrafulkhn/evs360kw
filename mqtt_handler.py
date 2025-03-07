
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
            logging.info("Connecting to MQTT broker...")
            result = self.client.connect("broker.hivemq.com", 1883, 60)
            if result == 0:
                logging.info("✓ Successfully connected to MQTT broker")
            else:
                logging.error(f"✗ Failed to connect to MQTT broker (code: {result})")
        except Exception as e:
            logging.error(f"✗ Connection error: {str(e)}")
            raise
    
    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected with result code {rc}")
        devices = ["D1", "D2", "D3", "central"]
        message_types = ["soc", "demand", "vehicle_status"]
        
        for device in devices:
            for gun_id in range(1, 3):
                for msg_type in message_types:
                    topic = f"vesec/{gun_id}/{msg_type}/{device}"
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
