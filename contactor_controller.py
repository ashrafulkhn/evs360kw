import logging
from typing import Dict, List

class Contactor:
    def __init__(self, contactor_id: int, gun_id: int):
        self.contactor_id = contactor_id
        self.gun_id = gun_id
        self.is_closed = False
        self.logger = logging.getLogger(__name__)

    def close(self):
        """Close the contactor (connect power to the gun)"""
        if not self.is_closed:
            # Implement actual contactor control here
            # This could be a GPIO signal, CAN message, or other control method
            self._control_contactor(True)
            self.is_closed = True
            self.logger.info(f"Closed contactor {self.contactor_id} for Gun {self.gun_id}")
            return True
        return False

    def open(self):
        """Open the contactor (disconnect power from the gun)"""
        if self.is_closed:
            # Implement actual contactor control here
            self._control_contactor(False)
            self.is_closed = False
            self.logger.info(f"Opened contactor {self.contactor_id} for Gun {self.gun_id}")
            return True
        return False

    def _control_contactor(self, close: bool):
        """
        Control physical contactor through appropriate interface

        This is a placeholder - implement your actual hardware control here,
        such as GPIO pins, serial commands, or CAN messages
        """
        command = "CLOSE" if close else "OPEN"
        self.logger.debug(f"Sending {command} command to contactor {self.contactor_id}")
        # Example: GPIO.output(self.contactor_id, GPIO.HIGH if close else GPIO.LOW)


class ContactorController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Dictionary to track which modules are connected to which guns
        self.connections = {}
        # Dictionary to track which modules are connected to which guns (reverse lookup)
        self.gun_to_modules = {i: [] for i in range(1, 7)}
        # Initialize contactors dictionary
        self.contactors = {}
        self._initialize_contactors()

    def _initialize_contactors(self):
        """Initialize contactors for all guns and power modules"""
        # For each gun (1-6), create contactors connecting to each power module (1-9)
        for gun_id in range(1, 7):
            self.contactors[gun_id] = {}
            for module_id in range(1, 10):
                contactor_id = gun_id * 100 + module_id  # Generate unique contactor ID
                self.contactors[gun_id][module_id] = Contactor(contactor_id, gun_id)

        self.logger.info(f"Initialized contactors for 6 guns and 9 power modules")

    def connect_gun_to_modules(self, gun_id: int, module_ids: List[int]):
        """
        Connect a gun to specified power modules

        Args:
            gun_id: The gun ID (1-6)
            module_ids: List of module IDs to connect
        """
        self.logger.info(f"Connecting Gun {gun_id} to modules: {module_ids}")
        # First disconnect any existing connections for this gun
        self.disconnect_gun(gun_id)

        # Connect the gun to each specified module
        self.gun_to_modules[gun_id] = []  # Reset the list for this gun
        for module_id in module_ids:
            # Logic to activate the contactor connecting gun_id to module_id
            # This would interface with hardware in a real system
            self.logger.debug(f"Activating contactor connecting Gun {gun_id} to Module {module_id}")
            # Track the connection
            self.connections[f"G{gun_id}M{module_id}"] = True
            self.gun_to_modules[gun_id].append(module_id)

    def disconnect_gun(self, gun_id: int):
        """
        Disconnect a gun from all power modules

        Args:
            gun_id: The gun ID (1-6)
        """
        self.logger.info(f"Disconnecting Gun {gun_id} from all modules")
        # Find all contactors involving this gun and deactivate them
        for key in list(self.connections.keys()):
            if key.startswith(f"G{gun_id}"):
                # Logic to deactivate the contactor
                self.logger.debug(f"Deactivating contactor {key}")
                # Remove the connection from tracking
                del self.connections[key]

        # Clear the modules list for this gun
        self.gun_to_modules[gun_id] = []

    def get_connected_modules(self, gun_id: int) -> List[int]:
        """Get list of module IDs connected to this gun"""
        return self.gun_to_modules.get(gun_id, [])