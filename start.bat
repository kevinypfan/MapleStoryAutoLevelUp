@echo off
echo 等待 10 秒後執行 Python 程式...
timeout /t 10 /nobreak

echo 執行 Python 程式
start "" python mapleStoryAutoLevelUp.py --map red_crab_beach_2 --monsters lorang --attack aoe_skill
start "" python fucus.py
