'''
KeyBoardController
'''
# Standard Import
import threading
import time

import pyautogui
import pygetwindow as gw
from pynput import keyboard

# Windows API imports (conditional)
try:
    import win32api
    import win32con
    import win32gui
    WINAPI_AVAILABLE = True
except ImportError:
    WINAPI_AVAILABLE = False

# DirectInput imports (conditional)
try:
    import pydirectinput
    DIRECTINPUT_AVAILABLE = True
except ImportError:
    DIRECTINPUT_AVAILABLE = False

# Interception imports (conditional)
try:
    from pyinterception import interception
    INTERCEPTION_AVAILABLE = True
except ImportError:
    INTERCEPTION_AVAILABLE = False

# Local import
from logger import logger

pyautogui.PAUSE = 0  # remove delay

class KeyBoardController():
    '''
    KeyBoardController
    '''
    def __init__(self, cfg, args):
        self.cfg = cfg
        self.command = ""
        self.t_last_up = 0.0
        self.t_last_down = 0.0
        self.t_last_toggle = 0.0
        self.t_last_screenshot = 0.0
        self.t_last_run = time.time()
        self.is_enable = True
        self.window_title = cfg.game_window_title
        self.attack_key = ""
        self.debounce_interval = 1 # second
        self.is_need_screen_shot = False
        self.is_need_toggle = False
        self.fps = 0
        self.fps_limit = 30
        self.t_last_buff_cast = [0] * len(self.cfg.buff_skill_keys)
        
        # Initialize control mode
        self.control_mode = cfg.keyboard_control_mode
        self.game_hwnd = None
        self.interception_context = None
        
        # Validate control mode
        if self.control_mode == "winapi" and not WINAPI_AVAILABLE:
            logger.warning("Windows API not available, falling back to pyautogui mode")
            self.control_mode = "pyautogui"
        elif self.control_mode == "directinput" and not DIRECTINPUT_AVAILABLE:
            logger.warning("DirectInput not available, falling back to pyautogui mode")
            self.control_mode = "pyautogui"
        elif self.control_mode == "interception" and not INTERCEPTION_AVAILABLE:
            logger.warning("Interception not available, falling back to pyautogui mode")
            self.control_mode = "pyautogui"
        elif self.control_mode == "auto_focus":
            # auto_focus mode uses pyautogui but automatically focuses window
            self.control_mode = "pyautogui"
            self.cfg.auto_focus_game_window = True
        
        # Find game window handle for winapi mode or auto_focus
        if self.control_mode == "winapi" or self.cfg.auto_focus_game_window:
            self._find_game_window()
        
        # Configure DirectInput if needed
        if self.control_mode == "directinput":
            pydirectinput.PAUSE = 0
        
        # Initialize Interception if needed
        if self.control_mode == "interception":
            try:
                self.interception_context = interception()
                logger.info("Interception driver initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Interception driver: {e}")
                logger.warning("Make sure to run as administrator and install Interception driver")
                self.control_mode = "pyautogui"

        # set up attack key
        if args.attack == "aoe_skill":
            self.attack_key = cfg.aoe_skill_key
        elif args.attack == "magic_claw":
            self.attack_key = cfg.magic_claw_key
        else:
            logger.error(f"Unexpected attack argument: {args.attack}")

        # Start keyboard control thread
        threading.Thread(target=self.run, daemon=True).start()

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

    def on_press(self, key):
        '''
        Handle key press events.
        '''
        try:
            # Handle regular character keys
            key.char
        except AttributeError:
            # Handle special keys
            if key == keyboard.Key.f1:
                if time.time() - self.t_last_toggle > self.debounce_interval:
                    self.toggle_enable()
                    self.t_last_toggle = time.time()
            elif key == keyboard.Key.f2:
                if time.time() - self.t_last_screenshot > self.debounce_interval:
                    self.is_need_screen_shot = True
                    self.t_last_screenshot = time.time()

    def toggle_enable(self):
        '''
        toggle_enable
        '''
        self.is_enable = not self.is_enable
        logger.info(f"Player pressed F1, is_enable:{self.is_enable}")

        # Make sure all key are released
        self.release_all_key()

    def _find_game_window(self):
        '''
        Find game window handle for Windows API control
        '''
        try:
            # Try exact match first
            self.game_hwnd = win32gui.FindWindow(None, self.window_title)
            
            # If not found, try partial match
            if not self.game_hwnd:
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if self.window_title in window_text or "MapleStory" in window_text:
                            windows.append((hwnd, window_text))
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    self.game_hwnd = windows[0][0]  # Use first match
                    logger.info(f"Found game window by partial match: {windows[0][1]} (handle: {self.game_hwnd})")
                else:
                    logger.warning(f"Could not find any MapleStory window")
            else:
                logger.info(f"Found game window handle: {self.game_hwnd}")
                
        except Exception as e:
            logger.error(f"Error finding game window: {e}")
            self.game_hwnd = None
    
    def _winapi_key_down(self, key):
        '''
        Send key down using Windows API
        '''
        if not self.game_hwnd:
            return
        
        # Convert key to virtual key code
        vk_code = self._get_vk_code(key)
        if vk_code:
            # Try multiple methods for better compatibility
            try:
                # Method 1: SendMessage (synchronous)
                win32api.SendMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
            except:
                try:
                    # Method 2: PostMessage (asynchronous)
                    win32api.PostMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                except:
                    # Method 3: Direct input simulation
                    win32api.keybd_event(vk_code, 0, 0, 0)
    
    def _winapi_key_up(self, key):
        '''
        Send key up using Windows API
        '''
        if not self.game_hwnd:
            return
        
        # Convert key to virtual key code
        vk_code = self._get_vk_code(key)
        if vk_code:
            # Try multiple methods for better compatibility
            try:
                # Method 1: SendMessage (synchronous)
                win32api.SendMessage(self.game_hwnd, win32con.WM_KEYUP, vk_code, 0)
            except:
                try:
                    # Method 2: PostMessage (asynchronous)
                    win32api.PostMessage(self.game_hwnd, win32con.WM_KEYUP, vk_code, 0)
                except:
                    # Method 3: Direct input simulation
                    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    def _get_interception_key_code(self, key):
        '''
        Convert key string to Interception key code
        '''
        # Interception scan codes (similar to DirectInput)
        key_map = {
            'left': 0x4B,
            'right': 0x4D,
            'up': 0x48,
            'down': 0x50,
            'space': 0x39,
            'ctrl': 0x1D,
            'alt': 0x38,
            'shift': 0x2A,
            'enter': 0x1C,
            'tab': 0x0F,
            'esc': 0x01,
        }
        
        if key in key_map:
            return key_map[key]
        elif len(key) == 1 and key.isalpha():
            # A-Z keys (scan codes 0x1E-0x2C for QWERTY layout)
            key_lower = key.lower()
            qwerty_layout = "qwertyuiopasdfghjklzxcvbnm"
            scan_codes = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19,  # qwertyuiop
                         0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26,           # asdfghjkl
                         0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32]                        # zxcvbnm
            if key_lower in qwerty_layout:
                return scan_codes[qwerty_layout.index(key_lower)]
        elif len(key) == 1 and key.isdigit():
            # Number keys 1-9, 0
            if key == '0':
                return 0x0B
            else:
                return 0x02 + int(key) - 1
        
        logger.warning(f"Unknown key for Interception: {key}")
        return None
    
    def _interception_key_down(self, key):
        '''
        Send key down using Interception
        '''
        if not self.interception_context:
            return
        
        scan_code = self._get_interception_key_code(key)
        if scan_code:
            try:
                self.interception_context.send_key(scan_code, interception.KEY_DOWN)
            except Exception as e:
                logger.error(f"Interception key down error: {e}")
    
    def _interception_key_up(self, key):
        '''
        Send key up using Interception
        '''
        if not self.interception_context:
            return
        
        scan_code = self._get_interception_key_code(key)
        if scan_code:
            try:
                self.interception_context.send_key(scan_code, interception.KEY_UP)
            except Exception as e:
                logger.error(f"Interception key up error: {e}")
    
    def _get_vk_code(self, key):
        '''
        Convert key string to Windows virtual key code
        '''
        key_map = {
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'space': win32con.VK_SPACE,
            'ctrl': win32con.VK_CONTROL,
            'alt': win32con.VK_MENU,
            'shift': win32con.VK_SHIFT,
        }
        
        if key in key_map:
            return key_map[key]
        elif len(key) == 1 and key.isalpha():
            return ord(key.upper())
        elif len(key) == 1 and key.isdigit():
            return ord(key)
        else:
            logger.warning(f"Unknown key: {key}")
            return None
    
    def _auto_focus_if_needed(self):
        '''
        Automatically focus game window if auto_focus is enabled
        '''
        if self.cfg.auto_focus_game_window and self.game_hwnd:
            try:
                win32gui.SetForegroundWindow(self.game_hwnd)
                win32gui.SetActiveWindow(self.game_hwnd)
            except:
                pass  # Ignore errors if focusing fails
    
    def key_down(self, key):
        '''
        Send key down based on control mode
        '''
        if self.cfg.debug_keyboard_control:
            logger.info(f"[DEBUG] Key down: {key} (mode: {self.control_mode}, hwnd: {self.game_hwnd})")
        
        # Auto focus if needed
        self._auto_focus_if_needed()
            
        if self.control_mode == "winapi":
            self._winapi_key_down(key)
        elif self.control_mode == "directinput":
            pydirectinput.keyDown(key)
        elif self.control_mode == "interception":
            self._interception_key_down(key)
        else:
            pyautogui.keyDown(key)
    
    def key_up(self, key):
        '''
        Send key up based on control mode
        '''
        if self.cfg.debug_keyboard_control:
            logger.info(f"[DEBUG] Key up: {key} (mode: {self.control_mode})")
            
        if self.control_mode == "winapi":
            self._winapi_key_up(key)
        elif self.control_mode == "directinput":
            pydirectinput.keyUp(key)
        elif self.control_mode == "interception":
            self._interception_key_up(key)
        else:
            pyautogui.keyUp(key)

    def press_key(self, key, duration=0.05):
        '''
        Simulates a key press for a specified duration
        '''
        self.key_down(key)
        time.sleep(duration)
        self.key_up(key)

    def disable(self):
        '''
        disable keyboard controlller
        '''
        self.is_enable = False

    def enable(self):
        '''
        enable keyboard controlller
        '''
        self.is_enable = True

    def set_command(self, new_command):
        '''
        Set keyboard command
        '''
        self.command = new_command
        # logger.info(f"Set command to {new_command}")

    def is_game_window_active(self):
        '''
        Check if the game window is currently the active (foreground) window.

        Returns:
        - True
        - False
        '''
        active_window = gw.getActiveWindow()
        return active_window is not None and self.window_title in active_window.title

    def release_all_key(self):
        '''
        Release all key
        '''
        self.key_up("left")
        self.key_up("right")
        self.key_up("up")
        self.key_up("down")
        # Also release attack keys to stop any ongoing attacks
        self.key_up(self.attack_key)


    def limit_fps(self):
        '''
        Limit FPS
        '''
        # If the loop finished early, sleep to maintain target FPS
        target_duration = 1.0 / self.fps_limit  # seconds per frame
        frame_duration = time.time() - self.t_last_run
        if frame_duration < target_duration:
            time.sleep(target_duration - frame_duration)

        # Update FPS
        self.fps = round(1.0 / (time.time() - self.t_last_run))
        self.t_last_run = time.time()
        # logger.info(f"FPS = {self.fps}")

    def is_in_buffer_skill_active_duration(self):
        '''
        is_in_buffer_skill_active_duration
        '''
        for t_last_cast in self.t_last_buff_cast:
            if time.time() - t_last_cast < self.cfg.buff_skill_active_duration:
                return True
        return False

    def run(self):
        '''
        run
        '''
        while True:
            # Check if game window is active
            if not self.is_enable or not self.is_game_window_active():
                self.limit_fps()
                continue

            # Buff skill
            if not self.is_in_buffer_skill_active_duration():
                for i, key in enumerate(self.cfg.buff_skill_keys):
                    cooldown = self.cfg.buff_skill_cooldown[i]
                    if time.time() - self.t_last_buff_cast[i] >= cooldown:
                        logger.info(f"[Buff] Press buff skill key: '{key}' (cooldown: {cooldown}s)")
                        self.press_key(key)
                        self.t_last_buff_cast[i] = time.time()  # Reset timer
                        break

            # check if is needed to release 'Up' key
            if time.time() - self.t_last_up > self.cfg.up_drag_duration:
                self.key_up("up")

            # check if is needed to release 'Down' key
            if time.time() - self.t_last_down > self.cfg.down_drag_duration:
                self.key_up("down")

            if self.command == "walk left":
                self.key_up("right")
                self.key_down("left")

            elif self.command == "walk right":
                self.key_up("left")
                self.key_down("right")

            elif self.command == "jump left":
                self.key_up("right")
                self.key_down("left")
                self.press_key(self.cfg.jump_key)
                self.key_up("left")

            elif self.command == "jump right":
                self.key_up("left")
                self.key_down("right")
                self.press_key(self.cfg.jump_key)
                self.key_up("right")

            elif self.command == "jump down":
                self.key_up("right")
                self.key_up("left")
                self.key_down("down")
                self.press_key(self.cfg.jump_key)
                self.key_up("down")

            elif self.command == "jump":
                self.key_up("left")
                self.key_up("right")
                self.press_key(self.cfg.jump_key)

            elif self.command == "up":
                self.key_up("down")
                self.key_down("up")
                self.t_last_up = time.time()

            elif self.command == "down":
                self.key_up("up")
                self.key_down("down")
                self.t_last_down = time.time()

            if self.command == "teleport left":
                self.key_up("right")
                self.key_down("left")
                self.press_key(self.cfg.teleport_key)

            elif self.command == "teleport right":
                self.key_up("left")
                self.key_down("right")
                self.press_key(self.cfg.teleport_key)

            elif self.command == "teleport up":
                self.key_down("up")
                self.press_key(self.cfg.teleport_key)
                self.key_up("up")

            elif self.command == "teleport down":
                self.key_down("down")
                self.press_key(self.cfg.teleport_key)
                self.key_up("down")

            elif self.command == "attack":
                self.press_key(self.attack_key)

            elif self.command == "attack left":
                self.key_up("right")
                self.key_down("left")
                time.sleep(self.cfg.character_turn_delay)  # Small delay for character to turn
                self.press_key(self.attack_key)
                self.key_up("left")

            elif self.command == "attack right":
                self.key_up("left")
                self.key_down("right")
                time.sleep(self.cfg.character_turn_delay)  # Small delay for character to turn
                self.press_key(self.attack_key)
                self.key_up("right")

            elif self.command == "stop":
                self.release_all_key()
                self.command = ""  # Clear command after stopping

            elif self.command == "heal":
                self.press_key(self.cfg.heal_key)
                self.command = ""

            elif self.command == "add mp":
                self.press_key(self.cfg.add_mp_key)
                self.command = ""

            else:
                pass

            self.limit_fps()
