
# Power Module to Gun Connection Documentation

## Overview

This document describes the dynamic allocation system for connecting 9 power modules to 6 charging guns. The system ensures optimal power distribution while maintaining these key constraints:

1. Each gun can receive power from multiple modules simultaneously
2. No module can be connected to more than one gun at a time
3. Guns with higher demand receive priority allocation
4. Each gun should receive power up to its maximum demand

## Module Allocation Strategy

### System Configuration
- **Number of Guns:** 6
- **Number of Power Modules:** 9
- **Module Power Capacity:** 40kW per module
- **Maximum Power per Gun:** 240kW (6 modules)

### Allocation Process

1. Sort guns by power demand (highest first)
2. For each gun in priority order:
   - Calculate modules needed based on demand
   - Assign available (unallocated) modules to the gun
   - Mark assigned modules as unavailable for other guns
3. Apply the assignments by activating necessary modules and configuring contactors

## Connection Paths Diagram

```
                     ╔═══════════════════╗
                     ║  POWER MODULES    ║
                     ╚═══════════════════╝
                     
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│ PM1 │   │ PM2 │   │ PM3 │   │ PM4 │   │ PM5 │   │ PM6 │   │ PM7 │   │ PM8 │   │ PM9 │
└──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘
   │         │         │         │         │         │         │         │         │
   │         │         │         │         │         │         │         │         │
   │         │         │         │         │         │         │         │         │
   ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                               CONTACTOR MATRIX                                      │
└───┬────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┘
    │        │        │        │        │        │        │        │        │
    │        │        │        │        │        │        │        │        │
┌───▼──┐  ┌──▼───┐  ┌─▼────┐  ┌▼─────┐  ┌▼─────┐  ┌▼─────┐
│ GUN1 │  │ GUN2 │  │ GUN3 │  │ GUN4 │  │ GUN5 │  │ GUN6 │
└──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘
```

## Example Allocations

### Scenario 1: Maximum Demand on Gun 1 Only
- Gun 1: 240kW (requires 6 modules)
- Other guns: 0kW

**Allocation:**
- Gun 1 receives modules PM1, PM2, PM3, PM4, PM5, PM6
- Modules PM7, PM8, PM9 remain available

### Scenario 2: Equal Demand Across All Guns
- Each gun demands 40kW (requires 1 module each)

**Allocation:**
- Gun 1 receives module PM1
- Gun 2 receives module PM2
- Gun 3 receives module PM3
- Gun 4 receives module PM4
- Gun 5 receives module PM5
- Gun 6 receives module PM6
- Modules PM7, PM8, PM9 remain available

### Scenario 3: Mixed High Demand
- Gun 1: 160kW (requires 4 modules)
- Gun 3: 120kW (requires 3 modules)
- Gun 5: 80kW (requires 2 modules)
- Other guns: 0kW

**Allocation:**
- Gun 1 receives modules PM1, PM2, PM3, PM4
- Gun 3 receives modules PM5, PM6, PM7
- Gun 5 receives modules PM8, PM9
- All modules are allocated

## Implementation Details

The system implements this allocation through:

1. **Demand Processor:** Calculates module requirements and assigns modules based on priority
2. **Contactor Controller:** Manages physical connections between guns and power modules
3. **Power Module Controller:** Activates/deactivates modules as needed

### Allocation Algorithm

```python
def _reassign_modules(self):
    # Sort guns by demand (highest first)
    sorted_guns = sorted(self.gun_demands.items(), key=lambda x: x[1], reverse=True)
    
    # Reset all assignments
    self.gun_module_assignments = {i: [] for i in range(1, 7)}
    
    # Track which modules are already assigned
    assigned_modules = set()
    
    # Assign modules to guns based on demand
    module_power = self.config.get_module_power_capacity()  # kW per module
    
    for gun_id, demand in sorted_guns:
        if demand <= 0:
            continue
        
        # Get the maximum power allowed for this gun from config
        max_allowed_power = self.config.get_gun_max_power(gun_id)
        
        # Limit demand to max allowed power
        capped_demand = min(demand, max_allowed_power)
        
        # Calculate how many modules this gun needs
        modules_needed = min(9, max(1, int((capped_demand + module_power - 1) // module_power)))
        modules_assigned = 0
        
        # Assign available modules
        for module_id in range(1, 10):  # 9 modules total
            if module_id not in assigned_modules and modules_assigned < modules_needed:
                self.gun_module_assignments[gun_id].append(module_id)
                assigned_modules.add(module_id)
                modules_assigned += 1
```

## Optimal Allocation Strategy

The system prioritizes:
1. Highest demand guns first (to ensure critical charging needs are met)
2. Module utilization efficiency (to maximize overall system capacity)
3. Dynamic reallocation when demands change

This approach ensures the most efficient use of power modules while meeting charging demands across all guns according to their priority.
