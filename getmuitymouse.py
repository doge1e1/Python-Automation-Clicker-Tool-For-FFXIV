import pyautogui
import sys
import json

# 強制設定輸出編碼防止亂碼
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=== 座標連續獲取工具 ===")
print("操作說明：")
print("1. 將滑鼠移至目標位置")
print("2. 按下 【Enter】 鍵紀錄當前座標")
print("3. 輸入 【q】 並按 Enter 結束並儲存檔案")
print("-" * 30)

coords_list = []

try:
    while True:
        count = len(coords_list) + 1
        user_input = input(f"請定位第 {count} 個點，按 Enter 記錄 (輸入 'q' 結束): ")
        
        # 檢查是否要結束
        if user_input.lower() == 'q':
            break
        
        # 獲取滑鼠當前位置
        x, y = pyautogui.position()
        coords_list.append([x, y]) # 使用 list 方便 JSON 儲存
        print(f">>> [已記錄] 點 {count}: ({x}, {y})")

    # 儲存到 JSON 檔案
    if len(coords_list) > 0:
        with open('coords.json', 'w', encoding='utf-8') as f:
            json.dump(coords_list, f, indent=4)
        print(f"\n[成功] 共紀錄 {len(coords_list)} 個座標，已匯出至 coords.json")
    else:
        print("\n[提示] 未記錄任何座標。")

except KeyboardInterrupt:
    print("\n\n[強制中斷] 程式已停止。")