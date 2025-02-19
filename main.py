import logging
from mqtt_handler import MQTTHandler


def setup_logging():
    logging.basicConfig(filename='debug.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    setup_logging()
    print("Device started.")
    mqtt_handler = MQTTHandler()
    mqtt_handler.run()


if __name__ == "__main__":
    main()
