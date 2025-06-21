# GPU 加速指南 (NVIDIA CUDA)

## 前置需求檢查

### 1. 硬體需求
- NVIDIA GPU (GTX 1050 以上建議)
- 至少 4GB VRAM
- CUDA Compute Capability 3.5+

### 2. 檢查 GPU 支援
```bash
# Windows
nvidia-smi

# 查看 CUDA 版本
nvcc --version
```

## 安裝步驟

### 1. 安裝 NVIDIA 驅動
- 下載最新 NVIDIA 驅動程式
- 建議版本：460.x 以上

### 2. 安裝 CUDA Toolkit
- 下載 CUDA 11.8 或 12.x
- 官網：https://developer.nvidia.com/cuda-downloads
- 安裝時選擇 "Custom" 並確保包含：
  - CUDA Toolkit
  - CUDA Samples
  - CUDA Documentation

### 3. 安裝 cuDNN
- 下載 cuDNN 8.x (對應 CUDA 版本)
- 官網：https://developer.nvidia.com/cudnn
- 解壓縮並複製到 CUDA 安裝目錄

### 4. 環境變數設定
```bash
# Windows
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8
set PATH=%CUDA_PATH%\bin;%PATH%

# Linux/Mac
export CUDA_PATH=/usr/local/cuda
export PATH=$CUDA_PATH/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH
```

### 5. 安裝 OpenCV with CUDA
```bash
# 卸載現有版本
pip uninstall opencv-python opencv-contrib-python

# 安裝 CUDA 版本 (可能需要從原始碼編譯)
pip install opencv-contrib-python==4.8.1.78

# 或使用預編譯版本
pip install opencv-python-headless==4.8.1.78
```

## 程式修改

### 1. 修改 requirements.txt
```txt
opencv-contrib-python==4.8.1.78
numpy
pyautogui
pynput
requests
pyyaml
windows-capture ; sys_platform == "win32"
pyobjc-framework-Quartz ; sys_platform == "darwin"
```

### 2. 修改 util.py
在檔案開頭加入 GPU 檢查：
```python
import cv2
import numpy as np

# GPU 支援檢查
USE_GPU = False
if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    USE_GPU = True
    print(f"CUDA devices found: {cv2.cuda.getCudaEnabledDeviceCount()}")
else:
    print("No CUDA devices found, using CPU")
```

修改 `find_pattern_sqdiff` 函數：
```python
def find_pattern_sqdiff(image, template, threshold=0.8, mask=None, debug=False):
    """GPU 加速版本的模板匹配"""
    global USE_GPU
    
    if USE_GPU:
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
                gpu_result = cv2.cuda.matchTemplate(gpu_image, gpu_template, cv2.TM_SQDIFF_NORMED, mask=gpu_mask)
            else:
                gpu_result = cv2.cuda.matchTemplate(gpu_image, gpu_template, cv2.TM_SQDIFF_NORMED)
            
            # 下載結果
            result = gpu_result.download()
            
        except Exception as e:
            print(f"GPU processing failed, fallback to CPU: {e}")
            # 降級使用 CPU
            if mask is not None:
                result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED, mask=mask)
            else:
                result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
    else:
        # CPU 版本
        if mask is not None:
            result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED, mask=mask)
        else:
            result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
    
    # 其餘處理邏輯保持不變
    locations = np.where(result <= (1.0 - threshold))
    matches = []
    for pt in zip(*locations[::-1]):
        matches.append([pt[0], pt[1], 1.0 - result[pt[1], pt[0]]])
    
    return matches
```

### 3. 修改 mapleStoryAutoLevelUp.py
在怪物偵測中加入 GPU 加速：
```python
def get_monsters_in_range(self, image, debug=False):
    """GPU 加速版本的怪物偵測"""
    global USE_GPU
    
    if USE_GPU:
        try:
            # 上傳圖片到 GPU
            gpu_image = cv2.cuda_GpuMat()
            gpu_image.upload(image)
            
            # GPU 形態學操作
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            gpu_kernel = cv2.cuda_GpuMat()
            gpu_kernel.upload(kernel)
            
            gpu_processed = cv2.cuda.morphologyEx(gpu_image, cv2.MORPH_CLOSE, gpu_kernel)
            processed_image = gpu_processed.download()
            
        except Exception as e:
            print(f"GPU morphology failed, using CPU: {e}")
            # CPU 降級
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            processed_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    else:
        # 原始 CPU 版本
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        processed_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    
    # 其餘邏輯保持不變
    # ... 原始代碼 ...
```

## 測試與驗證

### 1. 安裝後測試
```python
# test_gpu.py
import cv2
import numpy as np

print("OpenCV version:", cv2.__version__)
print("CUDA devices:", cv2.cuda.getCudaEnabledDeviceCount())

if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    # 簡單 GPU 測試
    img = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
    gpu_img = cv2.cuda_GpuMat()
    gpu_img.upload(img)
    
    # GPU 高斯模糊測試
    gpu_blurred = cv2.cuda.GaussianBlur(gpu_img, (15, 15), 0)
    result = gpu_blurred.download()
    
    print("GPU test successful!")
else:
    print("No GPU support found")
```

### 2. 效能測試
```bash
# 執行測試
python test_gpu.py

# 正常執行程式
python mapleStoryAutoLevelUp.py --map north_forst_training_ground_2 --monsters green_mushroom
```

## 預期效能提升

- **模板匹配**: 2-5x 加速
- **形態學操作**: 3-8x 加速
- **整體 FPS**: 30-60% 提升
- **CPU 使用率**: 降低 40-60%

## 故障排除

### 常見問題
1. **CUDA 找不到**: 檢查環境變數和驅動版本
2. **cuDNN 錯誤**: 確認 cuDNN 版本與 CUDA 相容
3. **記憶體不足**: 降低處理解析度或批次大小
4. **相容性問題**: 使用 CPU 降級機制

### 降級機制
程式會自動檢測 GPU 可用性，如果 GPU 處理失敗會自動降級到 CPU，確保程式正常運行。

## 注意事項

1. **記憶體管理**: GPU 記憶體有限，注意釋放不用的 GpuMat
2. **資料傳輸**: 避免頻繁的 CPU-GPU 資料傳輸
3. **相容性**: 某些 OpenCV 函數可能不支援 GPU
4. **除錯**: GPU 錯誤訊息可能不夠詳細

## 建議

- 先在測試環境安裝並測試
- 保留 CPU 版本作為備用
- 監控 GPU 使用率和溫度
- 定期更新驅動程式