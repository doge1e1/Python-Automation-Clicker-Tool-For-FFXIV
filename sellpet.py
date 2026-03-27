import pyautogui
import time

# 設定參數
START_X = 1191
START_Y = 224
ROWS = 7
COLS = 5
GAP = 55  # 間隔 55 像素

# 安全機制：滑鼠移到螢幕四角會強制停止腳本
pyautogui.FAILSAFE = True

print("=== 自動點擊腳本啟動 ===")
print(f"預計點擊範圍：{ROWS} 列 x {COLS} 行")
print("請在 3 秒內切換到目標視窗...")
time.sleep(3)

try:
    for r in range(ROWS):
        for c in range(COLS):
            # 計算當前座標
            # 當前 X = 起點X + (行數 * 間距)
            # 當前 Y = 起點Y + (列數 * 間距)
            current_x = START_X + (c * GAP)
            current_y = START_Y + (r * GAP)
            
            print(f"正在處理第 {r+1} 列, 第 {c+1} 行: ({current_x}, {current_y})")
            
            # 移動到該位置 (加上一點點隨機延遲看起來更自然)
            pyautogui.moveTo(current_x, current_y, duration=0.1)
            
            # 執行動作：右鍵點一下，再左鍵點一下
            pyautogui.rightClick()
            time.sleep(0.1)  # 右鍵後的微小停頓
            pyautogui.rightClick() # 預設就是左鍵
            pyautogui.rightClick()
            # 點擊完每個點的間隔時間（可視需求調整）
            
            
    print("\n[完成] 所有位置已點擊完畢。")

except KeyboardInterrupt:
    print("\n[停止] 使用者中斷程式。")