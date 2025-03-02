
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
        self.contactors: Dict[int, Dict[int, Contactor]] = {}
        self.logger = logging.getLogger(__name__)
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
        Connect a gun to specific power modules by closing appropriate contactors
        
        Args:
            gun_id: The gun ID (1-6)
            module_ids: List of module IDs to connect to this gun
        """
        if gun_id not in self.contactors:
            self.logger.error(f"Invalid gun ID: {gun_id}")
            return False
        
        # First disconnect any existing connections
        self.disconnect_gun(gun_id)
        
        # Connect to specified modules
        for module_id in module_ids:
            if module_id in self.contactors[gun_id]:
                self.contactors[gun_id][module_id].close()
            else:
                self.logger.error(f"Invalid module ID: {module_id} for gun {gun_id}")
        
        self.logger.info(f"Connected Gun {gun_id} to modules: {module_ids}")
        return True
    
    def disconnect_gun(self, gun_id: int):
        """Disconnect a gun from all power modules"""
        if gun_id not in self.contactors:
            self.logger.error(f"Invalid gun ID: {gun_id}")
            return False
        
        for module_id, contactor in self.contactors[gun_id].items():
            contactor.open()
        
        self.logger.info(f"Disconnected Gun {gun_id} from all modules")
        return True
    
    def get_connected_modules(self, gun_id: int) -> List[int]:
        """Get list of module IDs connected to this gun"""
        if gun_id not in self.contactors:
            return []
        
        return [module_id for module_id, contactor in self.contactors[gun_id].items() 
                if contactor.is_closed]
