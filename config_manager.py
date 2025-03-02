
import configparser
import logging
import os

class ConfigManager:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default if not exists"""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {str(e)}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config['PowerLimits'] = {
            'gun1_max_power': '240',
            'gun2_max_power': '240',
            'gun3_max_power': '240',
            'gun4_max_power': '240',
            'gun5_max_power': '240',
            'gun6_max_power': '240'
        }
        self.config['General'] = {
            'module_power_capacity': '40'
        }
        
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Created default configuration in {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error creating default configuration: {str(e)}")
    
    def get_gun_max_power(self, gun_id):
        """Get the maximum power allowed for a specific gun"""
        try:
            return float(self.config['PowerLimits'].get(f'gun{gun_id}_max_power', 240))
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error getting max power for gun {gun_id}: {str(e)}")
            return 240.0  # Default fallback
    
    def get_module_power_capacity(self):
        """Get the power capacity of each module"""
        try:
            return float(self.config['General'].get('module_power_capacity', 40))
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error getting module power capacity: {str(e)}")
            return 40.0  # Default fallback
    
    def save_config(self):
        """Save the current configuration to file"""
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def update_gun_max_power(self, gun_id, max_power):
        """Update the maximum power for a specific gun"""
        try:
            if gun_id < 1 or gun_id > 6:
                self.logger.error(f"Invalid gun ID: {gun_id}")
                return False
                
            self.config['PowerLimits'][f'gun{gun_id}_max_power'] = str(max_power)
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error updating max power for gun {gun_id}: {str(e)}")
            return False
