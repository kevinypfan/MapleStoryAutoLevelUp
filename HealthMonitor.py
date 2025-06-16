import threading
import time
import numpy as np
from logger import logger

class HealthMonitor:
    '''
    Independent health monitoring thread that can heal while other actions are running
    '''
    def __init__(self, cfg, args, kb_controller):
        self.cfg = cfg
        self.args = args
        self.kb = kb_controller
        self.running = False
        self.enabled = True
        self.thread = None
        
        # Health monitoring state
        self.hp_ratio = 1.0
        self.mp_ratio = 1.0
        self.last_heal_time = 0
        self.last_mp_time = 0
        
        # Frame data (will be updated by main thread)
        self.img_frame = None
        self.frame_lock = threading.Lock()
        self.frame_updated = threading.Event()
        
        # Pre-compute bar regions for better performance
        self.hp_slice = (slice(self.cfg.hp_bar_top_left[1], self.cfg.hp_bar_bottom_right[1]+1),
                        slice(self.cfg.hp_bar_top_left[0], self.cfg.hp_bar_bottom_right[0]+1))
        self.mp_slice = (slice(self.cfg.mp_bar_top_left[1], self.cfg.mp_bar_bottom_right[1]+1),
                        slice(self.cfg.mp_bar_top_left[0], self.cfg.mp_bar_bottom_right[0]+1))
        
        # Cache for computed bar sizes
        hp_bar_area = (self.cfg.hp_bar_bottom_right[1] - self.cfg.hp_bar_top_left[1] + 1) * \
                     (self.cfg.hp_bar_bottom_right[0] - self.cfg.hp_bar_top_left[0] + 1)
        mp_bar_area = (self.cfg.mp_bar_bottom_right[1] - self.cfg.mp_bar_top_left[1] + 1) * \
                     (self.cfg.mp_bar_bottom_right[0] - self.cfg.mp_bar_top_left[0] + 1)
        self.hp_total_pixels = hp_bar_area - 6
        self.mp_total_pixels = mp_bar_area - 6
        
    def start(self):
        '''
        Start health monitoring thread
        '''
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            logger.info("Health monitor started")
    
    def stop(self):
        '''
        Stop health monitoring thread
        '''
        self.running = False
        if self.thread:
            self.thread.join()
            logger.info("Health monitor stopped")
    
    def enable(self):
        '''
        Enable health monitoring
        '''
        self.enabled = True
        
    def disable(self):
        '''
        Disable health monitoring
        '''
        self.enabled = False
        
    def update_frame(self, img_frame):
        '''
        Update frame data from main thread - only copy HP/MP regions
        '''
        if not self.frame_lock.acquire(blocking=False):
            return  # Skip update if lock is busy
        
        try:
            # Only extract and store HP/MP bar regions instead of full frame
            hp_bar = img_frame[self.hp_slice]
            mp_bar = img_frame[self.mp_slice]
            self.img_frame = {'hp_bar': hp_bar.copy(), 'mp_bar': mp_bar.copy()}
            self.frame_updated.set()
        finally:
            self.frame_lock.release()
    
    def get_hp_mp_ratio(self):
        '''
        Extract HP and MP ratios from cached bar regions
        '''
        if self.img_frame is None:
            return 1.0, 1.0
            
        with self.frame_lock:
            if self.img_frame is None:
                return 1.0, 1.0
            hp_bar = self.img_frame['hp_bar']
            mp_bar = self.img_frame['mp_bar']
        
        # Optimized HP Detection using numpy operations
        hp_gray = np.mean(hp_bar, axis=2, dtype=np.uint8)
        empty_pixels_hp = np.sum((hp_bar[:,:,0] == hp_bar[:,:,1]) & (hp_bar[:,:,0] == hp_bar[:,:,2]))
        empty_pixels_hp = max(0, empty_pixels_hp - 6)
        hp_ratio = 1 - (empty_pixels_hp / max(1, self.hp_total_pixels))
        
        # Optimized MP Detection using numpy operations
        mp_gray = np.mean(mp_bar, axis=2, dtype=np.uint8)
        empty_pixels_mp = np.sum((mp_bar[:,:,0] == mp_bar[:,:,1]) & (mp_bar[:,:,0] == mp_bar[:,:,2]))
        empty_pixels_mp = max(0, empty_pixels_mp - 6)
        mp_ratio = 1 - (empty_pixels_mp / max(1, self.mp_total_pixels))
        
        return max(0, min(1, hp_ratio)), max(0, min(1, mp_ratio))
    
    def _monitor_loop(self):
        '''
        Main monitoring loop running in separate thread
        '''
        while self.running:
            try:
                if not self.enabled or self.args.disable_control:
                    time.sleep(0.2)
                    continue
                
                # Wait for frame update with timeout
                if not self.frame_updated.wait(timeout=0.1):
                    continue  # No new frame, skip this cycle
                
                self.frame_updated.clear()
                
                # Get current HP/MP ratios
                hp_ratio, mp_ratio = self.get_hp_mp_ratio()
                self.hp_ratio = hp_ratio
                self.mp_ratio = mp_ratio
                
                current_time = time.time()
                
                # Only check healing if HP is critically low (early exit optimization)
                if hp_ratio <= self.cfg.heal_ratio:
                    if current_time - self.last_heal_time > self.cfg.heal_cooldown:
                        self._heal()
                        self.last_heal_time = current_time
                        logger.info(f"Auto heal triggered, HP: {hp_ratio*100:.1f}%")
                
                # Only check MP if MP is low (early exit optimization)
                if mp_ratio <= self.cfg.add_mp_ratio:
                    if current_time - self.last_mp_time > self.cfg.mp_cooldown:
                        self._add_mp()
                        self.last_mp_time = current_time
                        logger.info(f"Auto MP triggered, MP: {mp_ratio*100:.1f}%")
                
                # Adaptive sleep based on health status
                if hp_ratio > 0.8 and mp_ratio > 0.8:
                    time.sleep(0.1)  # Sleep longer when health is good
                else:
                    time.sleep(0.05)  # Check more frequently when health is low
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                time.sleep(0.1)
    
    def _heal(self):
        '''
        Execute heal action
        '''
        try:
            self.kb.press_key(self.cfg.heal_key, 0.05)
        except Exception as e:
            logger.error(f"Heal action failed: {e}")
    
    def _add_mp(self):
        '''
        Execute MP recovery action
        '''
        try:
            self.kb.press_key(self.cfg.add_mp_key, 0.05)
        except Exception as e:
            logger.error(f"MP action failed: {e}")