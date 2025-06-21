# Single-threaded healing blocks other actions

## Problem

The current implementation handles healing synchronously in the main game loop, causing blocking behavior where the bot cannot heal while performing other actions.

### Issues:
- Cannot heal while attacking monsters
- Cannot heal while climbing ropes (`up`/`down` commands)  
- Cannot heal while jumping
- healing only triggers when main loop reaches HP, MP check

### Code Problem:
```python
elif command in ["up", "down", "jump right", "jump left"]:
    pass # Don't attack or heal while character is on rope or jumping
elif self.hp_ratio <= self.cfg.heal_ratio:
    command = "heal"
```

This explicitly prevents healing during movement actions.

## Solution

Implement independent health monitoring thread for concurrent healing.

**Fixed in:** https://github.com/KenYu910645/MapleStoryAutoLevelUp/pull/19