from mqtt_handler import MQTTHandler
from logger_config import setup_logging
import logging
import json


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
    # Get single gun data
    gun1_data = mqtt_handler.message_processor.get_gun_data(1)
    print(f"Gun 1 data: {gun1_data}")

    # Get all guns data
    all_data = get_all_guns_data(mqtt_handler)
    print(f"All guns data: {all_data}")
    mqtt_handler.run()


if __name__ == "__main__":
    main()
