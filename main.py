from mqtt_handler import MQTTHandler
from logger_config import setup_logging
import logging


def main():
    setup_logging()
    logging.info("=== MQTT Application Starting ===")
    logging.debug("Initializing components...")
    mqtt_handler = MQTTHandler()
    logging.info("Starting MQTT handler...")
    mqtt_handler.run()


if __name__ == "__main__":
    main()
