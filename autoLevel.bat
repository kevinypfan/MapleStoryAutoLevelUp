@echo off
rem ===================== 驗證參數 =====================
if "%~3"=="" (
    echo 用法: %~nx0 ^<nametag^> ^<map^> ^<attack^>
    echo 範例: %~nx0 zackfan the_road_of_time_1 aoe_skill
    exit /b 1
)

set "NAMETAG=%~1"
set "MAP=%~2"
set "ATTACK=%~3"
set "MONSTERS="

rem ===================== MAP → MONSTERS 對照 =====================
rem ★ 若日後要擴充，只要在這裡加一行即可
if /I "%MAP%"=="the_road_of_time_1"       set "MONSTERS=evolved_ghost"
if /I "%MAP%"=="forest_labyrinth_4"       set "MONSTERS=dark_stone_golem"
if /I "%MAP%"=="first_barrack"            set "MONSTERS=skeleton_officer,skeleton_soldier"
if /I "%MAP%"=="garden_of_red_2"          set "MONSTERS=red_cellion"
if /I "%MAP%"=="wushan_canyon"            set "MONSTERS=hogul,samiho"
if /I "%MAP%"=="iron_black_fattys_domain" set "MONSTERS=iron_boar"
if /I "%MAP%"=="chubby_park_2"            set "MONSTERS=iron_hook"
if /I "%MAP%"=="mushroom_hills"           set "MONSTERS=orange_mushroom,green_mushroom"
if /I "%MAP%"=="ruins_excavation_site_3"  set "MONSTERS=rocky_mask,wooden_mask"
if /I "%MAP%"=="ruins_excavation_site_1"  set "MONSTERS=ghost_stump,wooden_mask"
if /I "%MAP%"=="fire_land_2"              set "MONSTERS=fire_pig,dark_axe_stump"
if /I "%MAP%"=="land_of_wild_boar"        set "MONSTERS=wild_boar,dark_axe_stump"
if /I "%MAP%"=="blue_light_garden_2"      set "MONSTERS=grupin"
if /I "%MAP%"=="foggy_forest_for_mage"    set "MONSTERS=the_book_ghost"

if not defined MONSTERS (
    echo [錯誤] 不支援的 map: %MAP%
    exit /b 1
)

rem ===================== nametag → cfg =====================
rem 去掉 nametag 結尾的數字 (e.g. zackfan2 → zackfan)
for /f "tokens=1 delims=0123456789" %%A in ("%NAMETAG%") do set "CFG=%%A"

rem ===================== 執行 =====================
python mapleStoryAutoLevelUp.py ^
    --map %MAP% ^
    --monsters %MONSTERS% ^
    --attack %ATTACK% ^
    --nametag %NAMETAG% ^
    --cfg %CFG%
