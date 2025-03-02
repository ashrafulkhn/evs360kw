
# EV Charging Control System Documentation

## System Overview

This system manages power distribution for electric vehicle charging stations. It processes messages from multiple devices (D1, D2, D3) via MQTT, monitors gun status, and allocates power modules to guns based on vehicle demand.

## Architecture

The system is based on a modular architecture with the following components:

1. **MQTT Communication Layer**: Handles all messaging between devices and the central system
2. **Message Processing Layer**: Interprets MQTT messages and maps them to guns
3. **Power Management Layer**: Allocates power modules to guns based on demand
4. **Configuration Layer**: Manages system parameters and limits

## Components

### 1. MQTT Handler (`mqtt_handler.py`)
- Connects to broker.hivemq.com on port 1883
- Subscribes to topics in the format: `vesec/gun_id/message_type/device`
- Processes incoming messages and forwards them to the message processor
- Implements connection error handling and reconnection logic

### 2. Message Processor (`message_processor.py`)
- Maps device/topic gun IDs to actual gun numbers (6 guns total)
- Processes three types of messages:
  - SOC (State of Charge)
  - Demand (Power demand in kW)
  - Vehicle Status
- Routes data to the appropriate gun object

### 3. Gun Controller (`gun.py`)
- Maintains state information for each gun (1-6)
- Tracks SOC, demand, and status
- Triggers actions when values change
- Forwards demand changes to the Demand Processor

### 4. Demand Processor (`demand_processor.py`)
- Processes power demand changes from all guns
- Prioritizes demand allocation based on configurable rules
- Manages power module assignments
- Enforces maximum power limits per gun
- Coordinates module activation and contactor control

### 5. Power Module Controller (`power_module_controller.py`)
- Controls 9 power modules
- Activates/deactivates modules based on demand
- Manages communication with power modules via CAN bus
- Tracks total system power capacity and usage

### 6. Contactor Controller (`contactor_controller.py`)
- Manages physical connections between guns and power modules
- Controls contactors to connect/disconnect guns from modules
- Ensures proper electrical isolation between charging circuits

### 7. Configuration Manager (`config_manager.py`)
- Manages system configuration via config.ini
- Defines power limits for each gun
- Sets module power capacity

## Data Flow

```
                                                ┌────────────────┐
                                                │Configuration   │
                                                │Manager         │
                                                └────────┬───────┘
                                                         │
                                                         ▼
┌─────────┐     ┌──────────────┐     ┌────────────┐     ┌────────────────┐
│Devices  │────▶│MQTT Handler  │────▶│Message     │────▶│Gun Controller  │
│D1,D2,D3 │     │              │     │Processor   │     │                │
└─────────┘     └──────────────┘     └────────────┘     └────────┬───────┘
                                                                  │
                                                                  ▼
                                                         ┌────────────────┐
                                                         │Demand Processor│
                                                         └────────┬───────┘
                                                                  │
                                  ┌─────────────────────┬─────────┘
                                  │                     │
                         ┌────────▼─────────┐  ┌────────▼─────────┐
                         │Power Module      │  │Contactor         │
                         │Controller        │  │Controller        │
                         └──────────────────┘  └──────────────────┘
```

## Message Flow

1. Devices (D1, D2, D3) send MQTT messages with topic format `vesec/gun_id/message_type/device`
2. MQTT Handler receives messages and forwards to Message Processor
3. Message Processor:
   - Maps device gun_id to actual gun number
   - Updates gun state (SOC, demand, status)
4. When demand changes:
   - Gun forwards demand to Demand Processor
   - Demand Processor:
     - Checks against maximum allowed power
     - Calculates required modules
     - Assigns modules to guns
     - Activates needed modules via Power Module Controller
     - Connects guns to modules via Contactor Controller

## Power Allocation Process

1. **Power Demand Detection**:
   - System receives demand messages from vehicles
   - Each gun's demand is updated

2. **Module Assignment**:
   - Guns are prioritized by demand level (highest first)
   - Maximum power cap is applied per gun
   - Modules are assigned to guns based on need
   - Each module provides a fixed power capacity (40kW default)

3. **Physical Connection**:
   - Power modules are activated as needed
   - Contactors are closed to connect modules to guns
   - Guns without demand are disconnected

4. **Power Monitoring**:
   - System continuously monitors power usage
   - Reassigns modules when demand changes

## Configuration

The system uses `config.ini` to define power limits and module capacities:

```ini
[PowerLimits]
# Maximum power (in kW) allowed per gun
gun1_max_power = 240
gun2_max_power = 240
gun3_max_power = 240
gun4_max_power = 240
gun5_max_power = 240
gun6_max_power = 240

[General]
# Default module power capacity in kW
module_power_capacity = 40
```

## Logging

The system implements comprehensive logging via `logger_config.py`:
- Console logging (INFO level and above)
- File logging to debug.log (DEBUG level and above)
- Rotating log files (max 5MB per file, 3 backup files)

## Deployment

Deployment is managed via `deploy.py`:
- Pulls code from Git repository
- Manages application lifecycle
- Provides automatic updates

## Running the Application

The application is started using:
```bash
python main.py
```

This initializes all components and starts the MQTT client listening for messages.
