import os
import shutil

# Clear the __pycache__ directory
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    print("Cache cleared.")

from mqtt_handler import MQTTHandler
from logger_config import setup_logging
import logging
import json
import threading
import time


def monitor_gun_data(mqtt_handler):
    previous_states = {
        i: {
            'soc': None,
            'demand': None,
            'status': None
        }
        for i in range(1, 7)
    }
    
    display_counter = 0  # Counter to display allocation periodically

    while True:
        for gun_number in range(1, 7):
            gun = mqtt_handler.message_processor.guns[gun_number]
            prev_state = previous_states[gun_number]

            # Check each parameter
            if gun.soc != prev_state['soc']:
                gun.soc_changed(gun.soc)
                prev_state['soc'] = gun.soc

            if gun.demand != prev_state['demand']:
                gun.demand_changed(gun.demand)
                prev_state['demand'] = gun.demand

            if gun.status != prev_state['status']:
                gun.status_changed(gun.status)
                prev_state['status'] = gun.status

        # Display module and contactor allocation every 5 seconds
        display_counter += 1
        if display_counter >= 5:
            display_gun_allocations()
            display_counter = 0
            
        time.sleep(1)  # Check every second


def display_gun_allocations():
    """Display active guns with their power modules and closed contactors"""
    try:
        # Import needed modules
        from demand_processor import DemandProcessor
        from contactor_controller import ContactorController
        
        # Get instances (using similar approach as in Gun class)
        if not hasattr(display_gun_allocations, '_demand_processor'):
            display_gun_allocations._demand_processor = DemandProcessor()
        if not hasattr(display_gun_allocations, '_contactor_controller'):
            display_gun_allocations._contactor_controller = ContactorController()
        
        demand_processor = display_gun_allocations._demand_processor
        contactor_controller = display_gun_allocations._contactor_controller
        
        # Display header
        logging.info("=== CURRENT GUN ALLOCATIONS ===")
        
        # For each gun, display its allocation
        for gun_id in range(1, 7):
            # Get assigned modules from demand processor
            allocation = demand_processor.get_gun_power_allocation(gun_id)
            if 'modules_assigned' in allocation and allocation['modules_assigned']:
                # Get connected modules from contactor controller
                connected_modules = contactor_controller.get_connected_modules(gun_id)
                
                logging.info(f"Gun {gun_id}:")
                logging.info(f"  - Demand: {allocation.get('demand', 0)} kW")
                logging.info(f"  - Assigned modules: {allocation.get('modules_assigned', [])}")
                logging.info(f"  - Connected via contactors: {connected_modules}")
                logging.info(f"  - Total capacity: {allocation.get('total_capacity_kw', 0)} kW")
    except Exception as e:
        logging.error(f"Error displaying gun allocations: {str(e)}")


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
    monitor_thread = threading.Thread(target=monitor_gun_data,
                                      args=(mqtt_handler, ),
                                      daemon=True)
    monitor_thread.start()
    logging.info("Started monitoring thread")

    # Run MQTT handler
    mqtt_handler.run()


if __name__ == "__main__":
    main()
