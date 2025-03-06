import tkinter as tk
from tkinter import ttk, messagebox
import json

# global variable to resize the icons 
SUBSAMPLE = 30

class TimerFrame(ttk.Frame):
    """
    Each TimerFrame is an individual timer that contains:
      - Name
      - Formated time (HH:MM:SS)
      - Buttons: Start, Reset, Erase, Set Timer
    """
    def __init__(self, master, icon_start, icon_reset, icon_erase, icon_gear, **kwargs):
        super().__init__(master, **kwargs)
        # initial state
        self.name = "Timer"
        self.mode = "stopwatch"  # or "countdown"
        self.fixed_time = None   # initial value for countdown (in seconds)
        self.current_time = 0    # curren time (in seconds)
        self.is_running = False
        self.timer_job = None
        
        # icons 
        self.icon_start = icon_start
        self.icon_reset = icon_reset
        self.icon_erase = icon_erase
        self.icon_gear = icon_gear

        # labels 
        self.name_label = ttk.Label(self, text=self.name, font=("Helvetica", 14, "bold"), width=20)
        self.time_label = ttk.Label(self, text=self.format_time(self.current_time), font=("Helvetica", 18))

        # buttons       
        self.start_button = ttk.Button(self, image=self.icon_start, command=self.start)
        self.reset_button = ttk.Button(self, image=self.icon_reset, command=self.reset)
        self.erase_button = ttk.Button(self, image=self.icon_erase, command=self.erase_timer)
        self.set_timer_button = ttk.Button(self, image=self.icon_gear, command=self.open_set_timer)

        # layout in columns 
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.time_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # button order: Start, Reset, Erase, Set Timer
        self.start_button.grid(row=0, column=2, padx=5, pady=5)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5)
        self.erase_button.grid(row=0, column=4, padx=5, pady=5)
        self.set_timer_button.grid(row=0, column=5, padx=5, pady=5)

    def format_time(self, seconds):
        """Format time (in segundos) to HH:MM:SS."""
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def update_timer(self):
        """Update timer."""
        if self.is_running:
            if self.mode == "stopwatch":
                self.current_time += 1
            elif self.mode == "countdown":
                self.current_time -= 1
                if self.current_time <= 0:
                    self.current_time = 0
                    self.is_running = False
                    # turns green when the cooldown is over
                    self.name_label.config(foreground="green")
                    self.time_label.config(text=self.format_time(self.current_time))
                    return

            self.time_label.config(text=self.format_time(self.current_time))
            self.timer_job = self.after(1000, self.update_timer)

    def start(self):
        """Start the countdown (if not running)."""
        if not self.is_running:
            self.is_running = True
            self.update_timer()

    def reset(self):
        """
        Reset the timer for the initial state.
        If countdown, returns the defined value.
        If not, returns 00:00:00.
        Then, automatically restart the countdown.
        """
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.is_running = False

        # back to default color
        self.name_label.config(foreground="black")

        if self.mode == "countdown" and self.fixed_time is not None:
            self.current_time = self.fixed_time
        else:
            self.current_time = 0

        self.time_label.config(text=self.format_time(self.current_time))

        # restart the countdown
        self.is_running = True
        self.update_timer()

    def erase_timer(self):
        """Removes the timer from interface."""
        if self.is_running and self.timer_job is not None:
            self.after_cancel(self.timer_job)
        self.destroy()

    def open_set_timer(self):
        """Open a new window to configure a new timer."""
        self.set_timer_window = tk.Toplevel(self)
        self.set_timer_window.title("Config")
        
        self.set_timer_window.iconbitmap("boss-timer/assets/icons/tibia.ico")

        ttk.Label(self.set_timer_window, text="Timer name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.set_timer_window)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.set_timer_window, text="Hours:").grid(row=1, column=0, padx=5, pady=5)
        self.hour_spin = ttk.Spinbox(self.set_timer_window, from_=0, to=23, width=5, format="%02.0f")
        self.hour_spin.set("00")
        self.hour_spin.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.set_timer_window, text="Minutes:").grid(row=2, column=0, padx=5, pady=5)
        self.minute_spin = ttk.Spinbox(self.set_timer_window, from_=0, to=59, width=5, format="%02.0f")
        self.minute_spin.set("00")
        self.minute_spin.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.set_timer_window, text="Seconds:").grid(row=3, column=0, padx=5, pady=5)
        self.second_spin = ttk.Spinbox(self.set_timer_window, from_=0, to=59, width=5, format="%02.0f")
        self.second_spin.set("00")
        self.second_spin.grid(row=3, column=1, padx=5, pady=5)

        confirm_button = ttk.Button(self.set_timer_window, text="Confirm", command=self.set_timer)
        confirm_button.grid(row=4, column=0, columnspan=2, pady=10)

    def set_timer(self):
        """Define the timer (countdown mode)."""
        try:
            hrs = int(self.hour_spin.get())
            mins = int(self.minute_spin.get())
            secs = int(self.second_spin.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid values for the time.")
            return

        total_seconds = hrs * 3600 + mins * 60 + secs
        if total_seconds <= 0:
            messagebox.showerror("Error", "Time must be greater than zero.")
            return

        self.fixed_time = total_seconds
        self.current_time = total_seconds
        self.mode = "countdown"

        name_input = self.name_entry.get().strip()
        self.name = name_input if name_input else "Timer"
        self.name_label.config(text=self.name, foreground="black")
        self.time_label.config(text=self.format_time(self.current_time))
        self.set_timer_window.destroy()


class TimerTab(ttk.Frame):
    def __init__(self, master, icon_start, icon_reset, icon_erase, icon_gear, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # reference the main application
        self.icon_start = icon_start
        self.icon_reset = icon_reset
        self.icon_erase = icon_erase
        self.icon_gear = icon_gear

        self.timers_frame = ttk.Frame(self)
        self.timers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # buttons 
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=5)

        self.new_timer_button = ttk.Button(buttons_frame, text="New", command=self.add_timer)
        self.save_button = ttk.Button(buttons_frame, text="Save", command=self.app.save_all_presets)
        self.load_button = ttk.Button(buttons_frame, text="Load", command=self.app.load_all_presets)

        self.new_timer_button.pack(side=tk.LEFT, padx=5)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.load_button.pack(side=tk.LEFT, padx=5)

    def add_timer(self):
        """Creates a new timer in the interface and
           automatically resizes the window."""
        timer = TimerFrame(
                self.timers_frame,
                icon_start=self.icon_start,
                icon_reset=self.icon_reset,
                icon_erase=self.icon_erase,
                icon_gear=self.icon_gear
                )
        timer.pack(fill=tk.X, pady=5, padx=5)

        root = self.master.master  # notebook -> TimerApp (tk.Tk)
        root.update_idletasks()
        w = root.winfo_reqwidth()
        h = root.winfo_reqheight()
        root.geometry(f"{w}x{h}")
    
    def add_timer_from_data(self, timer_data):
        """Adds a timer based on the loaded data."""
        self.add_timer()
        new_timer = self.timers_frame.winfo_children()[-1]
        if isinstance(new_timer, TimerFrame):
            new_timer.name = timer_data['name']
            new_timer.name_label.config(text=timer_data['name'])

            new_timer.mode = timer_data.get('mode', 'stopwatch')
            if new_timer.mode == 'countdown':
                new_timer.fixed_time = timer_data['fixed_time']
                new_timer.current_time = timer_data.get('current_time', new_timer.fixed_time)
            else:
                new_timer.fixed_time = None
                new_timer.current_time = timer_data.get('current_time', 0)

            new_timer.time_label.config(text=new_timer.format_time(new_timer.current_time))

            if new_timer.is_running:
                new_timer.is_running = False
                if new_timer.timer_job is not None:
                    new_timer.after_cancel(new_timer.timer_job)
                    new_timer.timer_job = None

class TimerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("boss-timer")
        self.iconbitmap("boss-timer/assets/icons/tibia.ico")
        self.geometry("600x90")
        self.resizable(False, False)
        self.closing_tab = False

        style = ttk.Style(self)
        style.theme_use("clam")

        # load icons 
        self.icon_start = tk.PhotoImage(file="boss-timer/assets/images/start.png").subsample(SUBSAMPLE, SUBSAMPLE)
        self.icon_reset = tk.PhotoImage(file="boss-timer/assets/images/reset.png").subsample(SUBSAMPLE, SUBSAMPLE)
        self.icon_erase = tk.PhotoImage(file="boss-timer/assets/images/erase.png").subsample(SUBSAMPLE, SUBSAMPLE)
        self.icon_gear = tk.PhotoImage(file="boss-timer/assets/images/gear.png").subsample(SUBSAMPLE, SUBSAMPLE)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<Double-1>", self.on_tab_double_click)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.tab_count = 0
        self.plus_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plus_tab, text="+")
        self.create_tab()

    def create_tab(self, add_initial_timer=True):
        """Creates a new window without a initial timer."""
        self.tab_count += 1
        tab_name = f"Window {self.tab_count}"
        new_tab = TimerTab(
            self.notebook,
            icon_start=self.icon_start,
            icon_reset=self.icon_reset,
            icon_erase=self.icon_erase,
            icon_gear=self.icon_gear,
            app=self  
        )
        if add_initial_timer:
            new_tab.add_timer()

        # Insert before the "+" tab
        plus_index = self.notebook.index(self.plus_tab)
        self.notebook.insert(plus_index, new_tab, text=tab_name)
        self.notebook.select(new_tab)
        self.update_geometry()

    def save_all_presets(self):
        """Saves all tabs in the preset.json."""
        tabs_data = []
        for tab_id in self.notebook.tabs():
            if tab_id == str(self.plus_tab):
                continue
            tab = self.notebook.nametowidget(tab_id)
            tab_name = self.notebook.tab(tab_id, "text")
            timers_data = []
            for timer in tab.timers_frame.winfo_children():
                if isinstance(timer, TimerFrame):
                    timer_data = {
                        'name': timer.name,
                        'mode': timer.mode,
                        'fixed_time': timer.fixed_time,
                        'current_time': timer.current_time
                    }
                    timers_data.append(timer_data)
            tabs_data.append({'name': tab_name, 'timers': timers_data})

        try:
            with open('boss-timer/core/preset.json', 'w') as f:
                json.dump(tabs_data, f, indent=4)
            messagebox.showinfo("Success", "All presets saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save presets: {e}")

    def load_all_presets(self):
        """Loads all tabs saved in preset.json."""
        try:
            with open('boss-timer/core/preset.json', 'r') as f:
                tabs_data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No preset file found.")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid preset file.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {e}")
            return

        # closes all tabs
        for tab_id in self.notebook.tabs():
            if tab_id != str(self.plus_tab):
                self.notebook.forget(tab_id)

        # creates saved tabs
        for tab_data in tabs_data:
            self.create_tab(add_initial_timer=False)
            new_tab = self.notebook.nametowidget(self.notebook.select())
            self.notebook.tab(new_tab, text=tab_data['name'])
            for timer_data in tab_data['timers']:
                new_tab.add_timer_from_data(timer_data)

        self.update_geometry()

    def update_geometry(self):
        """Update the main window size."""
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}")

    def on_tab_changed(self, event):
        if self.closing_tab:
            return

        current_tab = self.notebook.select()
        if current_tab == str(self.plus_tab):
            self.create_tab()

    def on_tab_double_click(self, event):
        """Rename tab on double click."""
        x, y = event.x, event.y
        try:
            tab_id = self.notebook.index(f"@{x},{y}")
        except tk.TclError:
            return

        tab_text = self.notebook.tab(tab_id, "text")
        if not tab_text or tab_text == "+":
            return

        tab_bbox = self.notebook.bbox(tab_id)
        if not tab_bbox:
            return

        original_name = tab_text

        tab_x, tab_y, tab_width, tab_height = tab_bbox
        entry_x = tab_x + self.notebook.winfo_x() + 2
        entry_y = tab_y + self.notebook.winfo_y() + 2

        entry = ttk.Entry(self)
        entry.insert(0, original_name)
        entry.select_range(0, tk.END)
        entry.icursor(tk.END)
        entry.place(x=entry_x, y=entry_y, width=tab_width-4, height=tab_height-4)
        entry.focus_set()

        def update_name(event=None):
            current_text = entry.get().strip()
            self.notebook.tab(tab_id, text=current_text or " ")

        def confirm(event=None):
            final_text = entry.get().strip()
            if not final_text:
                final_text = original_name
            self.notebook.tab(tab_id, text=final_text)
            entry.destroy()

        def cancel(event=None):
            self.notebook.tab(tab_id, text=original_name)
            entry.destroy()

        entry.bind("<KeyRelease>", update_name)
        entry.bind("<Return>", confirm)
        entry.bind("<Escape>", cancel)
        entry.bind("<FocusOut>", cancel)

    def on_tab_right_click(self, event):
        """Menu to close window."""
        x, y = event.x, event.y
        try:
            tab_id = self.notebook.index("@%d,%d" % (x, y))
        except Exception:
            return
        if self.notebook.tab(tab_id, "text") == "+":
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Close window", command=lambda: self.close_tab(tab_id))
        menu.tk_popup(event.x_root, event.y_root)

    def close_tab(self, tab_id):
        """Closes the window."""
        self.closing_tab = True
        self.notebook.forget(tab_id)
        self.closing_tab = False

        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}")
