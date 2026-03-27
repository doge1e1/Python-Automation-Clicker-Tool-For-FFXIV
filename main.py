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
        self.root.title("自動助手")
        self.root.attributes("-topmost", True)
        self.root.geometry("400x700+50+50")
        
        self.is_running = False
        self.force_stop = False
        
        # --- 預設座標 ---
        self.coords = [[1549, 967], [1859, 968], [1900, 920]] 

        # --- 介面佈局 ---
        # 1. 模式選擇 (預設為雙按鈕)
        tk.Label(self.root, text="--- 模式選擇 ---", font=("", 10, "bold")).pack(pady=(10, 0))
        self.mode_var = tk.IntVar(value=2) 
        tk.Radiobutton(self.root, text="雙按鈕 (製作 -> 巨集1)", variable=self.mode_var, value=2, command=self.update_coords_ui).pack()
        tk.Radiobutton(self.root, text="三按鈕 (製作 -> 巨集1 -> 巨集2)", variable=self.mode_var, value=3, command=self.update_coords_ui).pack()

        # 2. 座標設定區
        tk.Label(self.root, text="--- 座標設定 ---", font=("", 10, "bold")).pack(pady=(10, 0))
        self.btn_get_coords = tk.Button(self.root, text="錄製座標 (請看終端機)", command=self.start_get_mouse_thread, bg="#2196F3", fg="white", width=25)
        self.btn_get_coords.pack(pady=5)
        self.label_coords_display = tk.Label(self.root, text="", fg="blue", font=("", 9), wraplength=350)
        self.label_coords_display.pack()

        # 3. 參數設定區
        tk.Label(self.root, text="--- 執行與延遲參數 ---", font=("", 10, "bold")).pack(pady=(10, 0))
        self.create_entry("執行總次數:", "entry_count", "10")
        self.create_entry("製作後等待 (秒):", "entry_p1_wait", "1.0")
        self.create_entry("巨集 1 等待時間 (秒):", "entry_wait_big", "20.0")
        self.create_entry("巨集 2 等待時間 (秒):", "entry_m1_wait", "20.0")

        # 4. 顯示區
        tk.Label(self.root, text="--- 執行進度 ---", font=("", 10, "bold")).pack(pady=(15, 0))
        self.label_status = tk.Label(self.root, text="就緒", font=("Microsoft JhengHei", 10), fg="green")
        self.label_status.pack(pady=2)
        self.label_step_count = tk.Label(self.root, text="", font=("Microsoft JhengHei", 10), fg="orange")
        self.label_step_count.pack(pady=2)
        self.label_total_time = tk.Label(self.root, text="", font=("Microsoft JhengHei", 10, "bold"), fg="blue")
        self.label_total_time.pack(pady=2)

        # 5. 控制按鈕
        self.btn_start = tk.Button(self.root, text="開始執行", command=self.start_automation_thread, bg="#4CAF50", fg="white", width=15)
        self.btn_start.pack(pady=5)
        self.btn_stop = tk.Button(self.root, text="終止腳本", command=self.stop_script, bg="#FF4C4C", fg="white", width=15, state=tk.DISABLED)
        self.btn_stop.pack(pady=5)

        self.load_initial_data()

    def create_entry(self, label_text, attr_name, default_val):
        frame = tk.Frame(self.root)
        frame.pack(pady=2)
        tk.Label(frame, text=label_text, width=22, anchor='e').pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=12, justify='center')
        entry.insert(0, default_val)
        entry.pack(side=tk.LEFT)
        setattr(self, attr_name, entry)

    def load_initial_data(self):
        if os.path.exists('coords.json'):
            try:
                with open('coords.json', 'r') as f:
                    saved = json.load(f)
                    if saved and len(saved) >= 2: self.coords = saved
            except: pass
        self.update_coords_ui()

    def update_coords_ui(self):
        names = ["製作", "巨集1", "巨集2"]
        mode = self.mode_var.get()
        display_list = []
        for i, c in enumerate(self.coords):
            if i < mode: # 僅顯示當前模式需要的座標
                display_list.append(f"{names[i]}:({c[0]},{c[1]})")
        self.label_coords_display.config(text="目前座標：\n" + " | ".join(display_list))

    def start_get_mouse_thread(self):
        self.btn_get_coords.config(state=tk.DISABLED, text="錄製中...")
        Thread(target=self.get_mouse_logic, daemon=True).start()

    def get_mouse_logic(self):
        target_count = self.mode_var.get()
        names = ["【開始製作】", "【巨集1】", "【巨集2】"]
        temp_coords = []
        try:
            for i in range(target_count):
                input(f"請移至 {names[i]}，按 Enter 記錄...")
                x, y = pyautogui.position()
                temp_coords.append([x, y])
            self.coords = temp_coords
            with open('coords.json', 'w') as f: json.dump(self.coords, f)
            self.root.after(0, self.update_coords_ui)
        finally:
            self.root.after(0, lambda: self.btn_get_coords.config(state=tk.NORMAL, text="錄製座標 (請看終端機)"))

    def start_automation_thread(self):
        if len(self.coords) < self.mode_var.get():
            self.update_status("座標不足！", "red")
            return
        self.is_running, self.force_stop = True, False
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        Thread(target=self.automation_logic, daemon=True).start()

    def automation_logic(self):
        try:
            count = int(self.entry_count.get())
            wait_p1 = float(self.entry_p1_wait.get())
            wait_m1_m2 = float(self.entry_wait_big.get()) 
            wait_final = float(self.entry_m1_wait.get())  
            mode = self.mode_var.get()

            cycle_time = (wait_p1 + wait_m1_m2 + (wait_final if mode == 3 else 0))

            # 初始準備倒數
            for i in range(3, 0, -1):
                if self.force_stop: return
                self.update_status(f"請準備...切換至遊戲視窗 ({i}s)", "blue")
                time.sleep(1)

            for i in range(1, count + 1):
                if self.force_stop: break
                total_remain_sec = (count - i) * cycle_time
                
                # 1. 點擊製作
                self.update_status(f"[{i}/{count}] 動作: 點擊製作", "green")
                pyautogui.click(self.coords[0][0], self.coords[0][1])
                pyautogui.click(self.coords[0][0], self.coords[0][1])
                self.countdown("製作後等待", wait_p1, total_remain_sec + (cycle_time - wait_p1))

                # 2. 點擊巨集 1
                if self.force_stop: break
                self.update_status(f"[{i}/{count}] 動作: 點擊巨集 1", "green")
                pyautogui.click(self.coords[1][0], self.coords[1][1])
                pyautogui.click(self.coords[1][0], self.coords[1][1])

                if mode == 2:
                    if i < count: self.countdown("等待下一輪", wait_m1_m2, total_remain_sec)
                else:
                    self.countdown("等待巨集 2 執行", wait_m1_m2, total_remain_sec + wait_final)
                    if self.force_stop: break
                    # 3. 點擊巨集 2
                    self.update_status(f"[{i}/{count}] 動作: 點擊巨集 2", "green")
                    pyautogui.click(self.coords[2][0], self.coords[2][1])
                    pyautogui.click(self.coords[2][0], self.coords[2][1])
                    if i < count: self.countdown("巨集 2 完畢，等待下一輪", wait_final, total_remain_sec)
            
            if not self.force_stop:
                self.update_status("任務完成！", "blue")
                self.label_step_count.config(text="")
                self.label_total_time.config(text="所有流程已結束")
                self.root.after(1500, self.reset_ui)
            else:
                self.reset_ui() # 如果是終止，直接重置 UI

        except Exception as e:
            self.update_status(f"錯誤: {e}", "red")
            self.reset_ui()

    def countdown(self, label, current_wait, total_remain_base):
        t = current_wait
        while t > 0:
            if self.force_stop: return # 立即中斷倒數
            self.label_step_count.config(text=f"{label}: {t:.1f}s")
            total_show = total_remain_base + t
            mins, secs = divmod(int(total_show), 60)
            self.label_total_time.config(text=f"預計總剩餘時間: {mins:02d}:{secs:02d}")
            time.sleep(0.1)
            t -= 0.1
        self.label_step_count.config(text="") 

    def update_status(self, msg, color="black"):
        self.label_status.config(text=msg, fg=color)

    def stop_script(self):
        """強化後的終止函數"""
        self.force_stop = True
        self.is_running = False
        print("\n[系統訊息] 終止指令已發送。")
        self.update_status("已手動終止", "red")
        self.label_step_count.config(text="正在停止...")
        self.label_total_time.config(text="停止計算")

    def reset_ui(self):
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.label_total_time.config(text="")
        self.label_step_count.config(text="")
        if self.force_stop:
            self.update_status("已終止並就緒", "red")
        else:
            self.update_status("就緒", "green")

if __name__ == "__main__":
    app = ClickerApp()
    app.root.mainloop()