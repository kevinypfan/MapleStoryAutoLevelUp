# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MapleStoryAutoLevelUp is a computer vision-based automation script for MapleStory Artale that uses template matching and image recognition to control gameplay without accessing game memory. The bot can automatically level up characters by following predefined routes, attacking monsters, and solving rune puzzles.

## Core Architecture

### Main Components

- **mapleStoryAutoLevelUp.py**: Core bot logic and main game loop containing the `MapleStoryBot` class
- **GameWindowCapturor.py**: Captures game window frames using Windows API for real-time image processing
- **KeyBoardController.py**: Handles simulated keyboard input and hotkey management
- **config/config.py**: Central configuration for all bot parameters, thresholds, and keyboard mappings
- **util.py**: Computer vision utilities including template matching and image processing functions
- **logger.py**: Logging system for debugging and monitoring bot behavior

### Key Systems

1. **Player Localization**: Uses name tag detection to track player position within game window
2. **Camera Localization**: Maps game camera position to predefined route maps for navigation
3. **Monster Detection**: Multiple detection modes (template matching, contour detection, health bar detection)
4. **Route Following**: Color-coded pixel navigation system for automated movement
5. **Rune Solving**: Automatic detection and solving of rune mini-games using arrow recognition

## Common Development Commands

### Running the Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Basic usage with map and monsters
python mapleStoryAutoLevelUp.py --map <map_name> --monsters <monster_list>

# Example commands
python mapleStoryAutoLevelUp.py --map north_forst_training_ground_2 --monsters green_mushroom,spike_mushroom
python mapleStoryAutoLevelUp.py --map fire_land_2 --monsters fire_pig,black_axe_stump

# Patrol mode (no predefined routes)
python mapleStoryAutoLevelUp.py --patrol --monsters evolved_ghost

# Debug mode (no keyboard control)
python mapleStoryAutoLevelUp.py --disable_control --map lost_time_1 --monsters evolved_ghost
```

### Map and Asset Structure

- **maps/**: Full-size route maps for camera localization
- **minimaps/**: Minimap-based routes (alternative navigation system)
- **monster/**: Monster template images for detection
- **rune/**: Arrow and rune images for puzzle solving
- Route images use color codes defined in `config.py` for movement commands

## Configuration Guidelines

The `Config` class contains all tunable parameters:

- **Detection thresholds**: Adjust `monster_diff_thres`, `nametag_diff_thres`, etc. for accuracy
- **Attack ranges**: Configure `magic_claw_range_x/y` and `aoe_skill_range_x/y` for combat
- **Keyboard mappings**: Update skill keys in the keyboard mapping section
- **Color codes**: Route navigation uses RGB color values for movement commands
- **Performance settings**: `fps_limit` and detection modes for optimization

## Development Notes

- The bot requires MapleStory to run in windowed mode at smallest resolution (752x1282)
- Replace `name_tag.png` with your character's actual name tag for proper player detection
- New maps require route images with color-coded navigation paths
- Monster detection supports multiple modes: template matching, contour detection, and health bar detection
- All coordinates and thresholds are calibrated for the specific game resolution