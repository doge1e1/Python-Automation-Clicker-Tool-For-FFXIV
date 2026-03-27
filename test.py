import pyautogui
import time
import json
import os
import sys
import tkinter as tk
from threading import Thread

# 強制設定輸出編碼
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class ClickerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自動點擊助手")
        self.root.attributes("-topmost", True)
        self.root.geometry("320x280+50+50") # 稍微加大寬度以容納文字
        
        self.is_running = False
        self.force_stop = False

        # --- 介面佈局 ---
        tk.Label(self.root, text="執行次數 (RUN_COUNT):").pack(pady=(10, 0))
        self.entry_count = tk.Entry(self.root, justify='center')
        self.entry_count.insert(0, "2")
        self.entry_count.pack()

        tk.Label(self.root, text="間隔秒數 (WAIT_SECONDS):").pack(pady=(10, 0))
        self.entry_wait = tk.Entry(self.root, justify='center')
        self.entry_wait.insert(0, "40")
        self.entry_wait.pack()

        self.label_status = tk.Label(self.root, text="請設定參數後按開始", font=("Microsoft JhengHei", 10), fg="gray")
        self.label_status.pack(pady=10)

        # 新增總計時間顯示標籤
        self.label_total_time = tk.Label(self.root, text="", font=("Microsoft JhengHei", 9), fg="blue")
        self.label_total_time.pack()

        self.btn_start = tk.Button(self.root, text="開始執行", command=self.start_thread, bg="#4CAF50", fg="white", width=15)
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(self.root, text="終止腳本", command=self.stop_script, bg="#FF4C4C", fg="white", width=15, state=tk.DISABLED)
        self.btn_stop.pack(pady=5)

    def update_status(self, msg, color="black", total_msg=""):
        self.label_status.config(text=msg, fg=color)
        self.label_total_time.config(text=total_msg)
        self.root.update()

    def stop_script(self):
        """處理終止邏輯"""
        self.force_stop = True
        self.is_running = False
        print("\n[系統訊息] 終止指令已發送，成功停止腳本並重置。")
        self.update_status("終止成功！", "red", "進程已手動取消")
        self.root.after(1000, self.reset_ui) 

    def start_thread(self):
        if not self.is_running:
            self.is_running = True
            self.force_stop = False
            self.btn_start.config(state=tk.DISABLED)
            self.entry_count.config(state=tk.DISABLED)
            self.entry_wait.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            
            t = Thread(target=self.automation_logic, daemon=True)
            t.start()

    def automation_logic(self):
        try:
            count = int(self.entry_count.get())
            wait_time = float(self.entry_wait.get())
            
            file_path = 'coords.json'
            if not os.path.exists(file_path):
                self.update_status("錯誤：找不到 coords.json", "red")
                self.reset_ui()
                return

            with open(file_path, 'r') as f:
                coords = json.load(f)
            
            btn_make, btn_gather = coords[0], coords[1]

            # 初始倒數
            for i in range(3, 0, -1):
                if self.force_stop: return
                self.update_status(f"請切換視窗... ({i}s)", "blue")
                time.sleep(1)

            for i in range(1, count + 1):
                if self.force_stop: break
                
                # 計算剩餘次數與預估剩餘總時間
                remain_cycles = count - i
                est_total_wait = (remain_cycles+1) * wait_time
                
                self.update_status(f"執行中 [{i}/{count}]", "green", f"剩餘次數: {remain_cycles} 次 | 預估剩餘: {est_total_wait:.0f}s")
                
                # 執行點擊
                pyautogui.click(btn_make[0], btn_make[1])
                pyautogui.click(btn_make[0], btn_make[1])
                
                # 動作間緩衝
                for _ in range(15):
                    if self.force_stop: return
                    time.sleep(0.1)

                pyautogui.click(btn_gather[0], btn_gather[1])
                pyautogui.click(btn_gather[0], btn_gather[1])

                # 循環間倒數
                if i < count:
                    remaining = wait_time
                    while remaining > 0:
                        if self.force_stop: return
                        # 同步顯示單次倒數與總剩餘時間
                        current_est = (remain_cycles - 1) * wait_time + remaining
                        self.update_status(
                            f"等待下一次 ({remaining:.1f}s)", 
                            "orange", 
                            f"剩餘次數: {remain_cycles} 次 | 總預估: {current_est:.0f}s"
                        )
                        time.sleep(0.1)
                        remaining -= 0.1
            
            if not self.force_stop:
                print("[完成] 腳本執行完畢")
                self.update_status("任務完成！", "blue", "所有循環已結束")
                time.sleep(1.5)
                self.reset_ui()

        except Exception as e:
            self.update_status(f"錯誤: {e}", "red")
            self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.entry_count.config(state=tk.NORMAL)
        self.entry_wait.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.label_total_time.config(text="")
        self.update_status("請設定參數後按開始", "gray")

if __name__ == "__main__":
    app = ClickerApp()
    app.root.mainloop()