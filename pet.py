import pyautogui
import time
import keyboard  # 新增鍵盤監聽套件

# 設定點擊座標
points = [
    (599, 301), (599, 301),
    (914, 615), (914, 615),
    (923, 693), (923, 693)
]

pyautogui.FAILSAFE = True

print("=== 自動點擊腳本 ===")
print("1. 按下 'q' 鍵可隨時【停止腳本】")
print("2. 將滑鼠快速甩到螢幕【左上角】也可強制停止")
print("腳本將在 3 秒後開始...")
time.sleep(3)

running = True

def stop_script():
    global running
    running = False
    print("\n[偵測到停止指令] 正在結束程式...")

# 設定按下 'q' 鍵時觸發 stop_script 函數
keyboard.add_hotkey('q', stop_script)

try:
    while running:
        for pt in points:
            if not running: break  # 每次點擊前檢查是否已停止
            
            pyautogui.click(pt[0], pt[1])
            print(f"點擊: {pt}")
            
            # 短暫延遲
            time.sleep(0.1)
        
        # 輪次間隔
        time.sleep(0.1)

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    print("腳本已完全停止。")