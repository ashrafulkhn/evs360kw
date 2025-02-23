from mqtt_handler import MQTTHandler
from logger_config import setup_logging
import logging
import json
import threading
import time


def monitor_gun_data(mqtt_handler):
    previous_data = {}
    while True:
        current_data = get_all_guns_data(mqtt_handler)
        if current_data != previous_data:
            print("\n=== Gun Data Update ===")
            print(current_data)
            previous_data = current_data
        time.sleep(1)  # Check every second


def get_all_guns_data(mqtt_handler):
    all_guns_data = {}
    for gun_number in range(1, 7):
        gun_data = mqtt_handler.message_processor.get_gun_data(gun_number)
        if gun_data:
            all_guns_data[f"Gun{gun_number}"] = gun_data
    return json.dumps(all_guns_data, indent=2)


def main():
    setup_logging()
    logging.info("=== MQTT Application Starting ===")
    logging.debug("Initializing components...")
    mqtt_handler = MQTTHandler()
    logging.info("Starting MQTT handler...")
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_gun_data, args=(mqtt_handler,), daemon=True)
    monitor_thread.start()
    logging.info("Started monitoring thread")
    
    # Run MQTT handler
    mqtt_handler.run()


if __name__ == "__main__":
    main()
