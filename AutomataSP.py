import time
import ctypes
import threading
import datetime
import customtkinter as ctk
import random
import winsound

# ================= PREVENCIÓN DE SUSPENSIÓN =================
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_AWAYMODE_REQUIRED = 0x00000040

def set_keep_awake(enabled):
    if enabled:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
    else:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

ctk.set_appearance_mode("dark")
user32 = ctypes.windll.user32

def execute_click_and_enter(repeat=False, clk=False, cv=False, ent=False, snd=False):
    executed_any = False
    
    def do_delay():
        if executed_any:
            time.sleep(random.uniform(0.5, 1.5))
            
    # 1. Mouse Click
    if clk:
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        time.sleep(1.0) 
        executed_any = True

    # 2. Control + V
    if cv:
        if not repeat or (repeat and cv):
            do_delay()
            user32.keybd_event(0x11, 0, 0, 0)
            user32.keybd_event(0x56, 0, 0, 0)
            user32.keybd_event(0x56, 0, 0x0002, 0)
            user32.keybd_event(0x11, 0, 0x0002, 0)
            time.sleep(0.1)
            executed_any = True
        
    # 3. Enter
    if ent:
        do_delay()
        user32.keybd_event(0x0D, 0, 0, 0)
        user32.keybd_event(0x0D, 0, 0x0002, 0)
        executed_any = True

    # 4. Sonido
    if snd:
        do_delay()
        winsound.Beep(1000, 300) 
        executed_any = True

class SchedulerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Programador click")
        self.geometry("480x380")
        self.resizable(False, False)
        self.configure(fg_color="#000000")
        
        self.running = False
        self.first_execution_done = False
        self.current_next_exec = datetime.datetime.now()
        self.following_exec = None

        self.frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # ====== COLUMNA IZQUIERDA ======
        self.lbl_real_time_title = ctk.CTkLabel(self.frame, text="         Tiempo Real", font=("Arial", 14, "bold"), text_color="#FFFFFF")
        self.lbl_real_time_title.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=(20, 5))

        self.real_time_var = ctk.StringVar()
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        self.real_time_var.set(hora_actual)
        
        self.entry_real_time = ctk.CTkEntry(self.frame, width=160, justify="center", font=("Courier New", 28), textvariable=self.real_time_var, state="disabled", text_color="#FFFFFF")
        self.entry_real_time.grid(row=1, column=0, sticky="w", padx=(20, 0), pady=5)

        self.countdown_label = ctk.CTkLabel(self.frame, text="", font=("Courier New", 38, "bold"), text_color="#ff4444")
        self.countdown_label.grid(row=2, column=0, sticky="w", padx=(20, 0), pady=10)

        # CONTENEDOR ESPECÍFICO PARA CHECKBOXES
        self.checkbox_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.checkbox_frame.grid(row=3, column=0, rowspan=4, sticky="sw", padx=(20, 0), pady=(0, 20))

        self.var_click = ctk.BooleanVar(value=False)
        self.var_ctrl_v = ctk.BooleanVar(value=False)
        self.var_enter = ctk.BooleanVar(value=False)
        self.var_sound = ctk.BooleanVar(value=False)

        cb_font = ("Arial", 16)
        
        self.cb1 = ctk.CTkCheckBox(self.checkbox_frame, text="Click", variable=self.var_click, font=cb_font)
        self.cb1.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.cb2 = ctk.CTkCheckBox(self.checkbox_frame, text="Control + v", variable=self.var_ctrl_v, font=cb_font)
        self.cb2.grid(row=1, column=0, sticky="w", pady=(10, 10))

        self.cb3 = ctk.CTkCheckBox(self.checkbox_frame, text="Enter", variable=self.var_enter, font=cb_font)
        self.cb3.grid(row=2, column=0, sticky="w", pady=(10, 10))

        self.cb4 = ctk.CTkCheckBox(self.checkbox_frame, text="Sonido", variable=self.var_sound, font=cb_font)
        self.cb4.grid(row=3, column=0, sticky="w", pady=(10, 0))

        # ====== COLUMNA DERECHA ======
        self.label = ctk.CTkLabel(self.frame, text="Hora de ejecución (HH:MM:SS):", font=("Arial", 14, "bold"), text_color="#FFFFFF")
        self.label.grid(row=0, column=1, sticky="e", padx=(0, 20), pady=(20, 5))

        self.entry_time = ctk.CTkEntry(self.frame, width=160, justify="center", font=("Courier New", 28))
        self.entry_time.insert(0, hora_actual)
        self.entry_time.grid(row=1, column=1, sticky="e", padx=(0, 20), pady=5)
        
        self.entry_time.bind("<MouseWheel>", self.on_scroll)
        self.entry_time.bind("<Key>", lambda e: self.validate_numeric_input(e, self.entry_time, is_rep=False))

        self.countdown_label_2 = ctk.CTkLabel(self.frame, text="", font=("Courier New", 38, "bold"), text_color="#ff4444")
        self.countdown_label_2.grid(row=2, column=1, sticky="e", padx=(0, 20), pady=10)

        ctk.CTkLabel(self.frame, text="Repetir cada (HHH:MM:SS):   ", font=("Arial", 12)).grid(row=3, column=1, sticky="e", padx=(0, 20), pady=(5, 0))
        
        self.entry_rep = ctk.CTkEntry(self.frame, width=160, justify="center", font=("Courier New", 24))
        self.entry_rep.insert(0, "000:00:00")
        self.entry_rep.grid(row=4, column=1, sticky="e", padx=(0, 20), pady=5)
        
        self.entry_rep.bind("<MouseWheel>", self.on_scroll_rep)
        self.entry_rep.bind("<Key>", lambda e: self.validate_numeric_input(e, self.entry_rep, is_rep=True))

        self.btn_start = ctk.CTkButton(self.frame, text="Programar", fg_color="#27ae60", width=160 , height=40, font=("Arial", 22, "bold"), command=self.toggle_scheduling)
        self.btn_start.grid(row=5, column=1, rowspan=2, sticky="se", padx=(0, 20), pady=(5, 20))

        self.update_countdown(None)

    def validate_numeric_input(self, event, entry_widget, is_rep=False):
        if event.keysym in ("Left", "Right", "Up", "Down", "Tab"):
            return None

        if event.keysym in ("BackSpace", "Delete"):
            return "break"

        if not event.char.isdigit():
            return "break"

        idx = entry_widget.index("insert")
        
        # Validar límites según si es campo de hora o repetición (HHH vs HH)
        if is_rep:
            if idx in (3, 6) or idx >= 9:
                return "break"
        else:
            if idx in (2, 5) or idx >= 8:
                return "break"

        current_text = list(entry_widget.get())
        max_limit = 9 if is_rep else 8
        if len(current_text) == max_limit:
            current_text[idx] = event.char
            new_text = "".join(current_text)
            
            if is_rep:
                try:
                    parts = new_text.split(":")
                    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                    if h == 0 and m == 0 and 0 < s < 6:
                        new_text = "000:00:06"
                except ValueError:
                    pass

            entry_widget.delete(0, "end")
            entry_widget.insert(0, new_text)
            entry_widget.icursor(idx + 1)
            
        return "break"

    def enforce_forbidden_range(self):
        try:
            current_rep = self.entry_rep.get().split(":")
            h, m, s = int(current_rep[0]), int(current_rep[1]), int(current_rep[2])
            if h == 0 and m == 0 and 0 < s < 6:
                self.entry_rep.delete(0, "end")
                self.entry_rep.insert(0, "000:00:00")
        except:
            pass

    def on_scroll(self, event):
        idx = self.entry_time.index(f"@{event.x}")
        current_time = self.entry_time.get().split(":")
        delta = 1 if event.delta > 0 else -1
        
        h, m, s = int(current_time[0]), int(current_time[1]), int(current_time[2])
        
        if idx <= 2: 
            h = (h + delta) % 24
        elif idx <= 5: 
            prev_m = m
            m = (m + delta) % 60
            if delta > 0 and prev_m == 59 and m == 0:
                h = (h + 1) % 24
            elif delta < 0 and prev_m == 0 and m == 59:
                if h > 0: h -= 1
        else: 
            prev_s = s
            s = (s + delta) % 60
            if delta > 0 and prev_s == 59 and s == 0:
                prev_m = m
                m = (m + 1) % 60
                if prev_m == 59 and m == 0:
                    h = (h + 1) % 24
            elif delta < 0 and prev_s == 0 and s == 59:
                if m > 0:
                    m -= 1
                elif m == 0 and h > 0:
                    m = 59
                    h -= 1
            
        self.entry_time.delete(0, "end")
        self.entry_time.insert(0, f"{h:02d}:{m:02d}:{s:02d}")
        self.entry_time.icursor(idx)

    def on_scroll_rep(self, event):
        idx = self.entry_rep.index(f"@{event.x}")
        current_rep = self.entry_rep.get().split(":")
        delta = 1 if event.delta > 0 else -1
        
        h, m, s = int(current_rep[0]), int(current_rep[1]), int(current_rep[2])
        
        if idx <= 3: 
            h = (h + delta) % 1000
        elif idx <= 6: 
            prev_m = m
            m = (m + delta) % 60
            if delta > 0 and prev_m == 59 and m == 0:
                h = (h + 1) % 1000
            elif delta < 0 and prev_m == 0 and m == 59:
                if h > 0: h -= 1
        else: 
            if h == 0 and m == 0:
                if s == 0 and delta > 0:
                    s = 6
                elif s == 6 and delta < 0:
                    s = 0
                else:
                    s = (s + delta) % 60
            else:
                prev_s = s
                s = (s + delta) % 60
                if delta > 0 and prev_s == 59 and s == 0:
                    prev_m = m
                    m = (m + 1) % 60
                    if prev_m == 59 and m == 0:
                        h = (h + 1) % 1000
                elif delta < 0 and prev_s == 0 and s == 59:
                    if m > 0:
                        m -= 1
                    elif m == 0 and h > 0:
                        m = 59
                        h -= 1
            
        self.entry_rep.delete(0, "end")
        self.entry_rep.insert(0, f"{h:03d}:{m:02d}:{s:02d}")
        
        self.enforce_forbidden_range()
        self.entry_rep.icursor(idx)

    def toggle_scheduling(self):
        self.enforce_forbidden_range()
        target_time = self.entry_time.get().strip()
        if len(target_time) != 8 or target_time.count(":") != 2:
            self.label.configure(text="Formato incorrecto. Usa HH:MM:SS", text_color="#ff4444")
            return
        
        now = datetime.datetime.now()
        target = datetime.datetime.strptime(target_time, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
        if target < now: target += datetime.timedelta(days=1)
        
        try:
            h, m, s = map(int, self.entry_rep.get().split(":"))
            total_seconds = h * 3600 + m * 60 + s
        except:
            total_seconds = 0

        if self.running:
            if not self.first_execution_done:
                self.current_next_exec = target
                self.next_execution_time = target
                if total_seconds > 0:
                    self.following_exec = self.current_next_exec + datetime.timedelta(seconds=total_seconds)
                else:
                    self.following_exec = None
            else:
                if total_seconds > 0:
                    self.following_exec = self.current_next_exec + datetime.timedelta(seconds=total_seconds)
                else:
                    self.following_exec = None
            return

        self.running = True
        self.first_execution_done = False
        set_keep_awake(True)
        self.btn_start.configure(text="Actualizar", fg_color="#d35400")
        
        self.label.configure(text="Esperando ejecución...", text_color="#FFFFFF")
        
        self.next_execution_time = target
        self.current_next_exec = target
        
        if total_seconds > 0:
            self.following_exec = self.current_next_exec + datetime.timedelta(seconds=total_seconds)
        else:
            self.following_exec = None
        
        threading.Thread(target=self.wait_and_execute, daemon=True).start()

    def format_duration(self, td):
        total_seconds = int(td.total_seconds())
        if total_seconds <= 0:
            return "00:00:00"
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_countdown(self, target_time_str):
        now = datetime.datetime.now()
        self.real_time_var.set(now.strftime("%H:%M:%S"))

        if self.running:
            diff1 = self.current_next_exec - now
            self.countdown_label.configure(text=self.format_duration(diff1))
            
            if self.following_exec is not None:
                diff2 = self.following_exec - now
                self.countdown_label_2.configure(text=self.format_duration(diff2))
            else:
                self.countdown_label_2.configure(text="")
        else:
            self.countdown_label.configure(text="")
            self.countdown_label_2.configure(text="")

        self.after(200, lambda: self.update_countdown(target_time_str))

    def wait_and_execute(self):
        self.first_execution_done = False
        
        while self.running and datetime.datetime.now() < self.current_next_exec:
            time.sleep(0.02)
            
        if self.running:
            self.first_execution_done = True
            
            try:
                h, m, s = map(int, self.entry_rep.get().split(":"))
                total_seconds = h * 3600 + m * 60 + s
            except:
                total_seconds = 0
                
            if total_seconds > 0:
                next_target = self.following_exec
                following_target = next_target + datetime.timedelta(seconds=total_seconds)
                
                self.current_next_exec = next_target
                self.following_exec = following_target
                self.next_execution_time = next_target
                
                threading.Thread(target=execute_click_and_enter, args=(
                    False, self.var_click.get(), self.var_ctrl_v.get(), self.var_enter.get(), self.var_sound.get()
                ), daemon=True).start()
                
                while self.running:
                    while self.running and datetime.datetime.now() < self.current_next_exec:
                        time.sleep(0.02)
                        
                    if self.running: 
                        try:
                            h, m, s = map(int, self.entry_rep.get().split(":"))
                            total_seconds = h * 3600 + m * 60 + s
                        except:
                            total_seconds = 0
                            
                        if total_seconds > 0:
                            next_target = self.following_exec
                            following_target = next_target + datetime.timedelta(seconds=total_seconds)
                            
                            self.current_next_exec = next_target
                            self.following_exec = following_target
                            self.next_execution_time = next_target
                            
                            threading.Thread(target=execute_click_and_enter, args=(
                                True, self.var_click.get(), self.var_ctrl_v.get(), self.var_enter.get(), self.var_sound.get()
                            ), daemon=True).start()
                        else:
                            break
            else:
                threading.Thread(target=execute_click_and_enter, args=(
                    False, self.var_click.get(), self.var_ctrl_v.get(), self.var_enter.get(), self.var_sound.get()
                ), daemon=True).start()

            self.running = False
            self.after(0, lambda: self.btn_start.configure(text="Programar", fg_color="#27ae60"))
            self.after(0, lambda: self.label.configure(text="Hora de ejecución (HH:MM:SS):", text_color="#FFFFFF"))
            set_keep_awake(False)

if __name__ == "__main__":
    app = SchedulerApp()
    app.mainloop()