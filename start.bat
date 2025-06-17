@echo off
echo 等待 10 秒後執行 Python 程式...
timeout /t 10 /nobreak

echo 執行 Python 程式
start "" python mapleStoryAutoLevelUp.py --map fire_land_2 --monsters dark_axe_stump_stand,dark_axe_stump_move,fire_boar_move,fire_boar_stand --attack aoe_skill
start "" python fucus.py
