
import logging
from typing import Dict, List

class PowerModule:
    def __init__(self, module_id: int, arbitration_id: int, power_capacity: float = 40.0):
        self.module_id = module_id
        self.arbitration_id = arbitration_id
        self.power_capacity = power_capacity  # in kW
        self.is_active = False
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        if not self.is_active:
            # CAN message to start the power module
            can_message = self._build_can_message(command="START")
            self._send_can_message(can_message)
            self.is_active = True
            self.logger.info(f"Started power module {self.module_id} with arbitration ID 0x{self.arbitration_id:X}")
            return True
        return False
    
    def stop(self):
        if self.is_active:
            # CAN message to stop the power module
            can_message = self._build_can_message(command="STOP")
            self._send_can_message(can_message)
            self.is_active = False
            self.logger.info(f"Stopped power module {self.module_id} with arbitration ID 0x{self.arbitration_id:X}")
            return True
        return False
    
    def _build_can_message(self, command: str) -> Dict:
        """Build CAN message format based on the command"""
        # This would be customized based on your CAN protocol
        message = {
            "arbitration_id": self.arbitration_id,
            "data": [0x01] if command == "START" else [0x00],
            "is_extended_id": True
        }
        return message
    
    def _send_can_message(self, message: Dict):
        """
        Send CAN message to the bus
        Note: This is a placeholder method that should be implemented 
        based on your CAN interface library (e.g., python-can)
        """
        # Placeholder for actual CAN message sending
        self.logger.debug(f"Sending CAN message: {message}")
        # In a real implementation, you would use your CAN interface:
        # can_bus.send(can.Message(arbitration_id=message['arbitration_id'], 
        #                          data=message['data'],
        #                          is_extended_id=message['is_extended_id']))


class PowerModuleController:
    def __init__(self):
        self.modules: List[PowerModule] = []
        self.current_active_modules = 0
        self.logger = logging.getLogger(__name__)
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize the 9 power modules with their arbitration IDs"""
        arbitration_ids = [0x01234, 0x02345, 0x03456, 0x04567, 0x05678, 
                          0x06789, 0x0789A, 0x089AB, 0x09ABC]
        
        for i, arb_id in enumerate(arbitration_ids, 1):
            self.modules.append(PowerModule(i, arb_id))
        
        self.logger.info(f"Initialized {len(self.modules)} power modules")
    
    def process_demand(self, demand: float):
        """
        Process the power demand and adjust active modules accordingly
        
        Args:
            demand: Power demand in kW
        """
        if demand <= 0:
            self._deactivate_all_modules()
            return
        
        # Calculate how many modules we need
        module_power = self.modules[0].power_capacity  # Assuming all modules have the same capacity
        modules_needed = min(len(self.modules), max(1, int((demand + module_power - 1) // module_power)))
        
        self.logger.info(f"Processing demand: {demand}kW, requires {modules_needed} modules")
        
        # Activate or deactivate modules as needed
        if modules_needed > self.current_active_modules:
            # Need to activate more modules
            for i in range(self.current_active_modules, modules_needed):
                self.modules[i].start()
        elif modules_needed < self.current_active_modules:
            # Need to deactivate some modules
            for i in range(modules_needed, self.current_active_modules):
                self.modules[i].stop()
        
        self.current_active_modules = modules_needed
        return self.current_active_modules
    
    def _deactivate_all_modules(self):
        """Deactivate all power modules"""
        for module in self.modules:
            module.stop()
        self.current_active_modules = 0
        self.logger.info("All power modules deactivated")
    
    def get_active_modules(self) -> List[PowerModule]:
        """Return a list of currently active modules"""
        return [module for module in self.modules if module.is_active]
    
    def get_total_available_power(self) -> float:
        """Return the total available power capacity in kW"""
        return sum(module.power_capacity for module in self.modules)
    
    def get_active_power_capacity(self) -> float:
        """Return the total active power capacity in kW"""
        return sum(module.power_capacity for module in self.modules if module.is_active)
