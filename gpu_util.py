"""
GPU 加速工具模組
提供 GPU/CPU 自動切換的 OpenCV 函數
"""

import cv2
import numpy as np
from logger import logger

class GPUManager:
    """GPU 管理器，處理 GPU/CPU 自動切換"""
    
    def __init__(self):
        self.use_gpu = False
        self.gpu_available = False
        self._initialize_gpu()
    
    def _initialize_gpu(self):
        """初始化 GPU 支援"""
        try:
            cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
            if cuda_devices > 0:
                self.gpu_available = True
                self.use_gpu = True
                logger.info(f"Found {cuda_devices} CUDA device(s), GPU acceleration enabled")
                
                # 測試 GPU 基本功能
                self._test_gpu_basic()
            else:
                logger.info("No CUDA devices found, using CPU only")
        except Exception as e:
            logger.warning(f"GPU initialization failed: {e}, using CPU only")
            self.gpu_available = False
            self.use_gpu = False
    
    def _test_gpu_basic(self):
        """測試 GPU 基本功能"""
        try:
            test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            gpu_img = cv2.cuda_GpuMat()
            gpu_img.upload(test_img)
            result = gpu_img.download()
            logger.info("GPU basic test passed")
        except Exception as e:
            logger.warning(f"GPU basic test failed: {e}, disabling GPU")
            self.use_gpu = False
    
    def toggle_gpu(self, enable=None):
        """手動切換 GPU 模式"""
        if enable is None:
            self.use_gpu = not self.use_gpu
        else:
            self.use_gpu = enable and self.gpu_available
        
        status = "enabled" if self.use_gpu else "disabled"
        logger.info(f"GPU acceleration {status}")
        return self.use_gpu

# 全域 GPU 管理器
gpu_manager = GPUManager()

def match_template_gpu(image, template, method=cv2.TM_SQDIFF_NORMED, mask=None):
    """
    GPU 加速的模板匹配函數
    自動降級到 CPU 如果 GPU 失敗
    """
    if gpu_manager.use_gpu:
        try:
            # 上傳到 GPU
            gpu_image = cv2.cuda_GpuMat()
            gpu_template = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            gpu_template.upload(template)
            
            # GPU 模板匹配
            if mask is not None:
                gpu_mask = cv2.cuda_GpuMat()
                gpu_mask.upload(mask)
                gpu_result = cv2.cuda.matchTemplate(gpu_image, gpu_template, method, mask=gpu_mask)
            else:
                gpu_result = cv2.cuda.matchTemplate(gpu_image, gpu_template, method)
            
            # 下載結果
            result = gpu_result.download()
            return result
            
        except Exception as e:
            logger.warning(f"GPU template matching failed: {e}, falling back to CPU")
            # 降級到 CPU
            pass
    
    # CPU 版本
    if mask is not None:
        return cv2.matchTemplate(image, template, method, mask=mask)
    else:
        return cv2.matchTemplate(image, template, method)

def gaussian_blur_gpu(image, ksize, sigmaX, sigmaY=0):
    """GPU 加速的高斯模糊"""
    if gpu_manager.use_gpu:
        try:
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            gpu_result = cv2.cuda.GaussianBlur(gpu_image, ksize, sigmaX, sigmaY=sigmaY)
            return gpu_result.download()
        except Exception as e:
            logger.warning(f"GPU Gaussian blur failed: {e}, falling back to CPU")
    
    # CPU 版本
    return cv2.GaussianBlur(image, ksize, sigmaX, sigmaY=sigmaY)

def morphology_ex_gpu(image, op, kernel, iterations=1):
    """GPU 加速的形態學操作"""
    if gpu_manager.use_gpu:
        try:
            gpu_image = cv2.cuda_GpuMat()
            gpu_kernel = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            gpu_kernel.upload(kernel)
            
            gpu_result = cv2.cuda.morphologyEx(gpu_image, op, gpu_kernel, iterations=iterations)
            return gpu_result.download()
        except Exception as e:
            logger.warning(f"GPU morphology failed: {e}, falling back to CPU")
    
    # CPU 版本
    return cv2.morphologyEx(image, op, kernel, iterations=iterations)

def resize_gpu(image, dsize=None, fx=None, fy=None, interpolation=cv2.INTER_LINEAR):
    """GPU 加速的圖片縮放"""
    if gpu_manager.use_gpu:
        try:
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            
            # 處理 fx, fy 參數
            if dsize is None and fx is not None and fy is not None:
                h, w = image.shape[:2]
                dsize = (int(w * fx), int(h * fy))
            
            gpu_result = cv2.cuda.resize(gpu_image, dsize, interpolation=interpolation)
            return gpu_result.download()
        except Exception as e:
            logger.warning(f"GPU resize failed: {e}, falling back to CPU")
    
    # CPU 版本
    if fx is not None or fy is not None:
        return cv2.resize(image, dsize, fx=fx, fy=fy, interpolation=interpolation)
    else:
        return cv2.resize(image, dsize, interpolation=interpolation)

def cvt_color_gpu(image, code):
    """GPU 加速的顏色空間轉換"""
    if gpu_manager.use_gpu:
        try:
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            gpu_result = cv2.cuda.cvtColor(gpu_image, code)
            return gpu_result.download()
        except Exception as e:
            logger.warning(f"GPU color conversion failed: {e}, falling back to CPU")
    
    # CPU 版本
    return cv2.cvtColor(image, code)

def bilateral_filter_gpu(image, d, sigmaColor, sigmaSpace):
    """GPU 加速的雙邊濾波"""
    if gpu_manager.use_gpu:
        try:
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            gpu_result = cv2.cuda.bilateralFilter(gpu_image, d, sigmaColor, sigmaSpace)
            return gpu_result.download()
        except Exception as e:
            logger.warning(f"GPU bilateral filter failed: {e}, falling back to CPU")
    
    # CPU 版本
    return cv2.bilateralFilter(image, d, sigmaColor, sigmaSpace)

def get_gpu_info():
    """獲取 GPU 資訊"""
    if not gpu_manager.gpu_available:
        return "No GPU available"
    
    try:
        device_count = cv2.cuda.getCudaEnabledDeviceCount()
        info = f"CUDA Devices: {device_count}\n"
        
        for i in range(device_count):
            props = cv2.cuda.DeviceInfo(i)
            info += f"Device {i}: {props.name()}\n"
            info += f"  Compute Capability: {props.majorVersion()}.{props.minorVersion()}\n"
            info += f"  Memory: {props.totalMemory() / 1024 / 1024:.0f} MB\n"
        
        return info
    except Exception as e:
        return f"Error getting GPU info: {e}"

def benchmark_gpu_vs_cpu(iterations=100):
    """比較 GPU 和 CPU 效能"""
    import time
    
    # 測試圖片
    test_image = np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8)
    template = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    
    results = {}
    
    # CPU 測試
    start_time = time.time()
    for _ in range(iterations):
        cv2.matchTemplate(test_image, template, cv2.TM_SQDIFF_NORMED)
    cpu_time = time.time() - start_time
    results['CPU'] = cpu_time
    
    # GPU 測試
    if gpu_manager.gpu_available:
        start_time = time.time()
        for _ in range(iterations):
            match_template_gpu(test_image, template)
        gpu_time = time.time() - start_time
        results['GPU'] = gpu_time
        results['Speedup'] = cpu_time / gpu_time if gpu_time > 0 else 0
    else:
        results['GPU'] = "Not available"
        results['Speedup'] = "N/A"
    
    return results

# 匯出主要函數
__all__ = [
    'gpu_manager',
    'match_template_gpu',
    'gaussian_blur_gpu',
    'morphology_ex_gpu',
    'resize_gpu',
    'cvt_color_gpu',
    'bilateral_filter_gpu',
    'get_gpu_info',
    'benchmark_gpu_vs_cpu'
]