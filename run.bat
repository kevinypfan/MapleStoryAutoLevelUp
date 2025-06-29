@echo off
if "%1"=="zackfan" (
    python mapleStoryAutoLevelUp.py --map the_road_of_time_1 --monsters evolved_ghost --attack aoe_skill --nametag zackfan --cfg zackfan
) else if "%1"=="zackfan2" (
    python mapleStoryAutoLevelUp.py --map forest_labyrinth_4 --monsters dark_stone_golem --attack aoe_skill --nametag zackfan --cfg zackfan
) else if "%1"=="zackfan3" (
    python mapleStoryAutoLevelUp.py --map first_barrack --monsters skeleton_officer,skeleton_soldier --attack aoe_skill --nametag zackfan --cfg zackfan
) else if "%1"=="mantalkouo" (
    python mapleStoryAutoLevelUp.py --map mushroom_hills --monsters orange_mushroom,green_mushroom --attack directional --nametag mantalkouo --cfg mantalkouo
) else if "%1"=="mantalkouo2" (
    python mapleStoryAutoLevelUp.py --map ruins_excavation_site_3 --monsters rocky_mask,wooden_mask --attack directional --nametag mantalkouo --cfg mantalkouo
) else if "%1"=="mantalkouo3" (
    python mapleStoryAutoLevelUp.py --map ruins_excavation_site_1 --monsters ghost_stump,wooden_mask --attack directional --nametag mantalkouo --cfg mantalkouo
) else if "%1"=="mantalkouo4" (
    python mapleStoryAutoLevelUp.py --map fire_land_2 --monsters fire_pig,dark_axe_stump --attack directional --nametag mantalkouo --cfg mantalkouo
) else if "%1"=="mantalkouo5" (
    python mapleStoryAutoLevelUp.py --map land_of_wild_boar --monsters wild_boar,dark_axe_stump --attack directional --nametag mantalkouo --cfg mantalkouo
) else if "%1"=="mantalkouo6" (
    python mapleStoryAutoLevelUp.py --map the_road_of_time_1 --monsters evolved_ghost --attack directional --nametag mantalkouo --cfg mantalkouo
) else (
    echo Unknown target: %1
    exit /b 1
)
