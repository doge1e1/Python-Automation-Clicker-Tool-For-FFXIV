import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import json
import os
from pynput import mouse, keyboard

class AutomationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("操作錄製器 (支援匯入匯出)")
        self.root.geometry("340x620") # 增加高度容納新按鈕

        self.events = []
        self.is_recording = False
        self.is_playing = False 
        
        # --- UI 介面 ---
        self.status_label = tk.Label(root, text="狀態: 待機中", fg="blue", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=10)

        # 操作提示區塊
        hint_frame = tk.LabelFrame(root, text="💡 錄製建議", padx=10, pady=10, fg="#555555")
        hint_frame.pack(fill="x", padx=20, pady=5)
        
        hint_text = "請將焦點目標設定在螢幕左邊\n角色位置請接近螢幕右邊"
        tk.Label(hint_frame, text=hint_text, justify="left", fg="#d9534f", font=("Arial", 9, "bold")).pack()

        # 錄製控制區塊
        rec_frame = tk.LabelFrame(root, text="🎥 錄製控制", padx=10, pady=5)
        rec_frame.pack(fill="x", padx=20, pady=5)

        self.rec_btn = tk.Button(rec_frame, text="🔴 開始錄製 (F9)", command=self.start_recording, bg="#ffcccc")
        self.rec_btn.pack(fill="x", pady=2)

        self.stop_rec_btn = tk.Button(rec_frame, text="⏹️ 停止錄製 (End)", command=self.stop_recording, state="disabled")
        self.stop_rec_btn.pack(fill="x", pady=2)

        # 檔案管理區塊 (新增)
        file_frame = tk.LabelFrame(root, text="📂 檔案管理", padx=10, pady=5)
        file_frame.pack(fill="x", padx=20, pady=5)

        self.save_btn = tk.Button(file_frame, text="💾 匯出錄製檔 (Save JSON)", command=self.save_to_json)
        self.save_btn.pack(fill="x", pady=2)

        self.load_btn = tk.Button(file_frame, text="📁 匯入錄製檔 (Load JSON)", command=self.load_from_json)
        self.load_btn.pack(fill="x", pady=2)

        # 播放參數設定
        play_frame = tk.LabelFrame(root, text="⚙️ 播放設定", padx=10, pady=5)
        play_frame.pack(fill="x", padx=20, pady=5)
        
        input_subframe = tk.Frame(play_frame)
        input_subframe.pack()
        
        tk.Label(input_subframe, text="播放次數:").grid(row=0, column=0, sticky="e")
        self.repeat_entry = tk.Entry(input_subframe, width=10)
        self.repeat_entry.insert(0, "1")
        self.repeat_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(input_subframe, text="間隔(秒):").grid(row=1, column=0, sticky="e")
        self.interval_entry = tk.Entry(input_subframe, width=10)
        self.interval_entry.insert(0, "1.0")
        self.interval_entry.grid(row=1, column=1, padx=5, pady=2)

        self.play_btn = tk.Button(play_frame, text="▶️ 開始播放", command=self.start_playback_thread, bg="#ccffcc")
        self.play_btn.pack(fill="x", pady=2)

        self.stop_play_btn = tk.Button(play_frame, text="🚫 停止播放 (DEL)", command=self.stop_playback, bg="#eeeeee", state="disabled")
        self.stop_play_btn.pack(fill="x", pady=2)

        # 設定全域熱鍵
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<f9>': self.start_recording,
            '<end>': self.stop_recording,
            '<delete>': self.stop_playback
        })
        self.hotkey_listener.start()

    # --- 檔案功能 ---
    def save_to_json(self):
        if not self.events:
            messagebox.showwarning("提示", "目前沒有錄製任何動作可供匯出。")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="儲存錄製檔"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.events, f, indent=4)
                messagebox.showinfo("成功", f"動作已成功儲存至:\n{file_path}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗: {e}")

    def load_from_json(self):
        if self.is_recording or self.is_playing: return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="選取錄製檔"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
                self.status_label.config(text=f"狀態: 已載入 {len(self.events)} 個動作", fg="green")
                messagebox.showinfo("成功", "錄製檔載入成功！")
            except Exception as e:
                messagebox.showerror("錯誤", f"讀取失敗: {e}")

    # --- 錄製邏輯 ---
    def start_recording(self):
        if self.is_recording or self.is_playing: return
        self.events = []
        self.is_recording = True
        self.start_time = time.time()
        self.rec_btn.config(state="disabled")
        self.stop_rec_btn.config(state="normal")
        self.status_label.config(text="狀態: 錄製中...", fg="red")

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.key_listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener.start()
        self.key_listener.start()

    def on_click(self, x, y, button, pressed):
        if self.is_recording:
            self.events.append({
                "type": "mouse", "x": x, "y": y,
                "button": str(button), "pressed": pressed,
                "time": time.time() - self.start_time
            })

    def on_press(self, key):
        if self.is_recording:
            if key == keyboard.Key.end: return
            key_data = key.char if hasattr(key, 'char') and key.char else str(key)
            self.events.append({
                "type": "key", "key": key_data, "time": time.time() - self.start_time
            })

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        if hasattr(self, 'mouse_listener'): self.mouse_listener.stop()
        if hasattr(self, 'key_listener'): self.key_listener.stop()
        self.rec_btn.config(state="normal")
        self.stop_rec_btn.config(state="disabled")
        self.status_label.config(text=f"狀態: 錄製完成 ({len(self.events)} 動作)", fg="green")

    # --- 播放邏輯 ---
    def start_playback_thread(self):
        if self.is_playing or self.is_recording: return
        if not self.events:
            messagebox.showwarning("提示", "請先錄製或匯入操作檔")
            return
        self.is_playing = True
        self.stop_play_btn.config(state="normal")
        self.play_btn.config(state="disabled")
        threading.Thread(target=self.run_playback, daemon=True).start()

    def stop_playback(self):
        if self.is_playing:
            self.is_playing = False
            self.status_label.config(text="狀態: 已強制停止", fg="orange")

    def run_playback(self):
        try:
            repeats = int(self.repeat_entry.get())
            interval = float(self.interval_entry.get())
        except:
            self.is_playing = False
            return

        mouse_ctrl = mouse.Controller()
        key_ctrl = keyboard.Controller()
        
        count = 0
        while self.is_playing:
            if repeats != 0 and count >= repeats: break
            count += 1
            self.status_label.config(text=f"播放中: 第 {count} 次")
            
            last_time = 0
            for ev in self.events:
                if not self.is_playing: break
                time.sleep(ev["time"] - last_time)
                last_time = ev["time"]

                if ev["type"] == "mouse":
                    mouse_ctrl.position = (ev["x"], ev["y"])
                    btn = mouse.Button.left if "left" in ev["button"] else mouse.Button.right
                    if ev["pressed"]: mouse_ctrl.press(btn)
                    else: mouse_ctrl.release(btn)
                elif ev["type"] == "key":
                    k_str = ev["key"]
                    try:
                        if k_str.startswith("Key."):
                            k_obj = getattr(keyboard.Key, k_str.split(".")[1])
                            key_ctrl.press(k_obj); key_ctrl.release(k_obj)
                        elif k_str.startswith("<") and k_str.endswith(">"):
                            vk_code = int(k_str[1:-1])
                            k_obj = keyboard.KeyCode.from_vk(vk_code)
                            key_ctrl.press(k_obj); key_ctrl.release(k_obj)
                        else:
                            key_ctrl.press(k_str); key_ctrl.release(k_str)
                    except: pass
            
            for _ in range(int(interval * 10)):
                if not self.is_playing: break
                time.sleep(0.1)
        
        self.is_playing = False
        self.play_btn.config(state="normal")
        self.stop_play_btn.config(state="disabled")
        if count >= repeats and repeats != 0:
            self.status_label.config(text="狀態: 播放完畢", fg="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationTool(root)
    root.mainloop()