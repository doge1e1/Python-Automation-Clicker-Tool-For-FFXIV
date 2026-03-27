import pyautogui
import sys
import json  # 引入 json 處理檔案

# 強制設定輸出編碼防止亂碼
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("=== 座標獲取並儲存工具 ===")
print("操作說明：")
print("1. 定位【製作按鈕】，按 Enter")
print("2. 定位【聚集位置】，按 Enter")
print("3. 輸入 'q' 結束並儲存檔案")
print("-" * 30)

coords_list = []

try:
    while len(coords_list) < 2:  # 我們只需要兩個點
        label = "製作按鈕" if len(coords_list) == 0 else "聚集位置"
        user_input = input(f"請定位【{label}】，按 Enter 記錄 (q 結束): ")
        
        if user_input.lower() == 'q':
            break
        
        x, y = pyautogui.position()
        coords_list.append((x, y))
        print(f">>> 已記錄 {label}: ({x}, {y})")

    # 儲存到 JSON 檔案
    if len(coords_list) == 2:
        with open('coords.json', 'w') as f:
            json.dump(coords_list, f)
        print("\n[成功] 座標已匯出至 coords.json")
    else:
        print("\n[警告] 記錄點數不足，未更新檔案。")

except KeyboardInterrupt:
    pass
