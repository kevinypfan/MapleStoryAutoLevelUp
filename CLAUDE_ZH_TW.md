# CLAUDE.md (繁體中文版)

此檔案為 Claude Code (claude.ai/code) 在此專案中工作時提供指導。

## 專案概述

MapleStoryAutoLevelUp 是一個專為楓之谷 Artale 設計的電腦視覺自動化腳本，使用模板匹配和圖像識別技術來控制遊戲玩法，無需存取遊戲記憶體。機器人可以透過遵循預定義路線、攻擊怪物和解決符文謎題來自動升級角色。

## 核心架構

### 主要元件

- **mapleStoryAutoLevelUp.py**: 核心機器人邏輯和主遊戲迴圈，包含 `MapleStoryBot` 類別
- **GameWindowCapturor.py**: 使用 Windows API 擷取遊戲視窗畫面，用於即時圖像處理
- **KeyBoardController.py**: 處理模擬鍵盤輸入和快捷鍵管理
- **config/config.py**: 所有機器人參數、閾值和鍵盤對應的中央設定檔
- **util.py**: 電腦視覺工具，包括模板匹配和圖像處理功能
- **logger.py**: 用於除錯和監控機器人行為的日誌系統

### 關鍵系統

1. **玩家定位**: 使用名牌檢測來追蹤玩家在遊戲視窗中的位置
2. **鏡頭定位**: 將遊戲鏡頭位置對應到預定義的路線地圖以進行導航
3. **怪物檢測**: 多種檢測模式（模板匹配、輪廓檢測、血條檢測）
4. **路線跟隨**: 使用顏色編碼像素導航系統進行自動移動
5. **符文解謎**: 使用箭頭識別自動檢測和解決符文小遊戲

## 常用開發指令

### 執行機器人
```bash
# 安裝相依性
pip install -r requirements.txt

# 基本使用方式，指定地圖和怪物
python mapleStoryAutoLevelUp.py --map <地圖名稱> --monsters <怪物清單>

# 範例指令
python mapleStoryAutoLevelUp.py --map north_forst_training_ground_2 --monsters green_mushroom,spike_mushroom
python mapleStoryAutoLevelUp.py --map fire_land_2 --monsters fire_pig,black_axe_stump

# 巡邏模式（無預定義路線）
python mapleStoryAutoLevelUp.py --patrol --monsters evolved_ghost

# 除錯模式（無鍵盤控制）
python mapleStoryAutoLevelUp.py --disable_control --map lost_time_1 --monsters evolved_ghost

# 背景執行模式（無視窗顯示）
python mapleStoryAutoLevelUp.py --background --map cloud_balcony --monsters brown_windup_bear,pink_windup_bear

# 使用專用背景執行腳本
python run_background.py --map cloud_balcony --monsters brown_windup_bear,pink_windup_bear
```

### 地圖和資源結構

- **maps/**: 用於鏡頭定位的全尺寸路線地圖
- **minimaps/**: 基於小地圖的路線（替代導航系統）
- **monster/**: 用於檢測的怪物模板圖像
- **rune/**: 用於謎題解決的箭頭和符文圖像
- 路線圖像使用 `config.py` 中定義的顏色代碼來執行移動指令

## 設定指南

`Config` 類別包含所有可調整的參數：

- **檢測閾值**: 調整 `monster_diff_thres`、`nametag_diff_thres` 等以提高準確性
- **攻擊範圍**: 為戰鬥設定 `magic_claw_range_x/y` 和 `aoe_skill_range_x/y`
- **鍵盤對應**: 在鍵盤對應區段更新技能按鍵
- **顏色代碼**: 路線導航使用 RGB 顏色值執行移動指令
- **效能設定**: `fps_limit` 和檢測模式用於優化

## 開發注意事項

- 機器人需要楓之谷以視窗模式執行且使用最小解析度 (752x1282)
- 請將 `name_tag.png` 替換為您角色的實際名牌以進行正確的玩家檢測
- 新地圖需要帶有顏色編碼導航路徑的路線圖像
- 怪物檢測支援多種模式：模板匹配、輪廓檢測和血條檢測
- 所有座標和閾值都是針對特定遊戲解析度校準的

## 支援的地圖

1. 北部森林訓練場2 (north_forst_training_ground_2)
2. 火焰之地2 (fire_land_2)
3. 螞蟻洞2 (ant_cave_2)
4. 雲彩露臺 (cloud_balcony)
5. 遺失的時間1 (lost_time_1)

## 支援的怪物

1. 火肥肥 (fire_pig)
2. 綠菇菇 (green_mushroom)
3. 刺菇菇 (spike_mushroom)
4. 殭屍菇菇 (zombie_mushroom)
5. 黑斧木妖 (black_axe_stump)
6. 褐色發條熊 (brown_windup_bear)
7. 粉色發條熊 (pink_windup_bear)
8. 進化妖魔 (evolved_ghost)

## 背景執行模式

機器人支援完全背景執行，無需顯示任何視窗：

### 背景執行方法

**方法一：使用背景執行腳本**
```bash
python run_background.py --map <地圖名稱> --monsters <怪物清單> --attack <攻擊方式>
```

**方法二：使用背景旗標**
```bash
python mapleStoryAutoLevelUp.py --background --map <地圖名稱> --monsters <怪物清單> --attack <攻擊方式>
```

**方法三：永久設定**
在 `config/config.py` 中設定 `show_debug_windows = False`

### 背景模式特色

- ✅ 不顯示任何偵錯視窗
- ✅ 不需要遊戲視窗聚焦
- ✅ 可在執行其他應用程式時運作
- ✅ 仍可使用 F1（暫停/繼續）和 F2（截圖）快捷鍵
- ✅ 所有活動記錄於控制台
- ✅ 使用 Ctrl+C 停止機器人

### 範例

```bash
# 雲彩露臺背景執行
python run_background.py --map cloud_balcony --monsters brown_windup_bear,pink_windup_bear --attack magic_claw

# 遺失的時間1背景執行
python run_background.py --map lost_time_1 --monsters evolved_ghost --attack aoe_skill
```

## 系統需求

- Windows 11
- Python 3.12
- OpenCV 4.11
- 楓之谷必須以視窗模式執行並調整為最小視窗大小
- 背景模式下無需保持遊戲視窗聚焦