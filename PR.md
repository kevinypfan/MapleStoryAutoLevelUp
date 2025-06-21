# feat: Add threaded health monitoring for concurrent healing

## Summary
- Add independent health monitoring thread that can heal while attacking/moving
- Improve bot responsiveness by separating healing logic from main game loop
- Add cooldown timers to prevent healing spam

## Changes
- **New**: `HealthMonitor.py` - Independent thread for HP/MP monitoring and healing
- **Updated**: `config.py` - Added heal/MP cooldown settings (0.5 second each)
- **Updated**: `mapleStoryAutoLevelUp.py` - Integrated health monitor, removed blocking healing logic

## Benefits
- Bot can now heal while attacking or moving (non-blocking)
- Better performance with dedicated health monitoring thread
- Prevents healing spam with cooldown timers

## Test Plan
- [ ] Test healing triggers at low HP while attacking
- [ ] Test MP recovery while moving
- [ ] Verify cooldown prevents spam

### Test Plan 測試說明

#### 1. Test healing triggers at low HP while attacking
**測試低血量時攻擊中自動治療**
- 讓角色血量降到 50% 以下
- 確認機器人正在攻擊怪物
- 觀察是否會自動按下治療鍵（不中斷攻擊動作）
- 驗證角色可以同時攻擊和治療

#### 2. Test MP recovery while moving  
**測試移動中自動回魔**
- 讓角色魔力降到 50% 以下
- 確認機器人正在移動或跟隨路線
- 觀察是否會自動按下回魔鍵（不中斷移動）
- 驗證角色可以邊走邊喝魔水

#### 3. Verify cooldown prevents spam
**驗證冷卻時間防止技能濫用**
- 手動將血量/魔力調到很低
- 觀察治療/回魔動作的間隔時間
- 確認每次治療間隔至少 0.5 秒
- 驗證不會連續快速按鍵造成浪費

🤖 Generated with [Claude Code](https://claude.ai/code)