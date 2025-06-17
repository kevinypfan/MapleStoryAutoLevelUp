import win32gui
import win32con
import time

def focus_window_by_title(title_keyword):
    """根據視窗標題關鍵字聚焦視窗"""
    def enum_callback(hwnd, results):
        window_text = win32gui.GetWindowText(hwnd)
        if win32gui.IsWindowVisible(hwnd) and title_keyword.lower() in window_text.lower():
            results.append((hwnd, window_text))
        return True
    
    results = []
    win32gui.EnumWindows(enum_callback, results)
    
    if results:
        hwnd, title = results[0]
        print(f"找到視窗: {title}")
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return True
    else:
        print(f"找不到包含 '{title_keyword}' 的視窗")
        return False

game_window_title = 'MapleStory Worlds-Artale (繁體中文版)'

# 使用範例
time.sleep(10)  # 等待 10 秒
focus_window_by_title(game_window_title)  # 聚焦記事本視窗
# focus_window_by_title("Chrome")  # 聚焦 Chrome 瀏覽器
# focus_window_by_title("Visual Studio Code")  # 聚焦 VS Code
