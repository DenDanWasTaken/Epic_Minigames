import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import time
from style import StyleManager

##--Для розташування вікон по центру--##
def center_window(window, parent):
    window.update_idletasks()

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    win_width = window.winfo_width()
    win_height = window.winfo_height()

    x = parent_x + (parent_width // 2) - (win_width // 2)
    y = parent_y + (parent_height // 2) - (win_height // 2)

    window.geometry(f"+{x}+{y}")
##--Головне та контекстне меню--##
class BarMenu(tk.Menu):
    def __init__(self, master, lang):
        super().__init__(master)
        master.config(menu=self)
        self.master = master
        self.on_menu = lambda cmd: None
        self.lang = lang

        self.setup_barmenu()

    def setup_barmenu(self):
        # clear old menu
        self.delete(0, "end")

        self.game_menu = tk.Menu(self, tearoff=0)
        self.opt_menu = tk.Menu(self, tearoff=0)
        self.hist_menu = tk.Menu(self, tearoff=0)

        lang = self.lang

        self.add_cascade(label=lang["new_game"], menu=self.game_menu)
        self.add_cascade(label=lang["options"], menu=self.opt_menu)
        self.add_cascade(label=lang["history"], menu=self.hist_menu)
        self.add_command(label=lang["exit"], command=lambda: self.handle_command("Exit"))

        self.master.bind("<Escape>", lambda e: self.handle_command("Exit"))

        self.build_game_submenus(lang)

        self.opt_menu.add_command(
            label=lang["language"],
            command=lambda: self.handle_command("Language")
        )

        self.opt_menu.add_command(
            label=f"{lang['custom']} {lang['difficulty'].lower()}",
            command=lambda: self.handle_command("Custom Difficulty")
        )

        self.hist_menu.add_command(
            label=lang["view_scores"],
            command=lambda: self.handle_command("History")
        )

    def build_game_submenus(self, lang):
        games = [
            ("sorting_game", "DragDrop"),
            ("memory_match", "Memory"),
            ("aim_trainer", "AimTrainer"),
            ("reaction_game", "Reaction"),
            ("typing_game", "Typing")
        ]

        difficulties = ["Easy", "Medium", "Hard", "Custom"]

        for key, game_id in games:
            sub_menu = tk.Menu(self.game_menu, tearoff=0)
            self.game_menu.add_cascade(label=lang[key], menu=sub_menu)

            for diff in difficulties:
                sub_menu.add_command(
                    label=lang[diff.lower()],
                    command=lambda g=game_id, d=diff: self.handle_command(f"{g}_{d}")
                )

    def rebuild_barmenu(self, new_lang):
        self.lang = new_lang
        self.setup_barmenu()

    def handle_command(self, command):
        if self.on_menu:
            self.on_menu(command)

##--Вікно для змін мов--##
class LanguageWindow(tk.Toplevel):
    def __init__(self, master, current_lang, lang_list, on_save, lang):
        super().__init__(master)
        self.title(lang["language_settings_title"])
        self.geometry("250x200")

        container = ttk.Frame(self, padding=20)
        container.pack(expand=True)
        
        self.transient(master)
        self.grab_set() # Requirement 9: Makes it a proper custom dialog
        
        # Requirement 6: Using labels and radiobuttons
        ttk.Label(container, text=lang["language_select"], font=("Helvetica", 10, "bold")).pack(pady=10)
        
        self.lang_var = tk.StringVar(value=current_lang)
        
        for language in lang_list:
            ttk.Radiobutton(container, text=language, variable=self.lang_var, value=language).pack(anchor="w", padx=50)

        # Requirement 2: Button reaction
        ttk.Button(container, text=lang["apply"], 
                   command=lambda: self.handle_command(on_save)).pack(pady=20)
        
        center_window(self, master)

    def handle_command(self, on_save):
        on_save(self.lang_var.get())
        self.destroy()

##--Вікно з історією очків--##
class HistoryWindow(tk.Toplevel):
    def __init__(self, master, history, on_delete, on_export, on_import, on_sort, lang):
        super().__init__(master)
        self.lang = lang
        self.title(self.lang["history_window_title"])
        self.geometry("700x400")
        
        self.transient(master)
        self.grab_set() # Makes it a proper custom dialog

        self.sort_reverse=False

        self.columns = ( "user", "game", "difficulty", "time", "date", "score")
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.treeview = ttk.Treeview(tree_frame, columns=self.columns, show="headings")
        scrollbar.config(command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        self.treeview.pack(side="left", fill="both", expand=True)

        self.treeview.configure(yscrollcommand=scrollbar.set)

        column_widths = {"user": 80, "game": 100, "difficulty": 80, "time": 60, "date": 120, "score": 60}

        for col in self.columns:
            self.treeview.heading(col, text=self.lang[col], command=lambda c=col: self.handle_sort(c, on_sort))
            self.treeview.column(col, width=column_widths.get(col, 100), anchor="center", stretch=True)

        self.render(history)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        self.btn_import = ttk.Button(btn_frame, text=self.lang["import_button"], command=lambda: self.handle_import(on_import))
        self.btn_import.pack(side="left", padx=20)
        self.btn_export = ttk.Button(btn_frame, text=self.lang["export_button"], command=lambda: self.handle_export(on_export))
        self.btn_export.pack(side="right", padx=20)
        self.btn_delete = ttk.Button(btn_frame, text=self.lang["delete_button"], command=lambda: self.handle_delete(on_delete))
        self.btn_delete.pack(side="left")

        center_window(self, master)

    def render(self, history, index=0):
        # Clear existing items
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        # Insert history
        for record in history:
            self.treeview.insert("", "end", values=(
                record["user"], record["game"], record["difficulty"], 
                record["time"], record["date"], record["score"]
            ))
        self.set_selection(index)

    def update_headings(self, active_column, reverse, on_sort):
        for col in self.columns:
            arrow = ""

            if col == active_column:
                arrow = " ↓" if reverse else " ↑"

            self.treeview.heading(col, text=self.lang[col] + arrow, command=lambda c=col: self.handle_sort(c, on_sort))

    def handle_delete(self, on_delete):
        index = self.get_selection()
        if index is None:
            return
        on_delete(index)

    def handle_import(self, on_import):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            # The controller will handle the import and return the updated history
            updated_history = on_import(filepath)
            if updated_history is not None:
                self.render(updated_history)

    def handle_export(self, on_export):
        default_name = f"game_history_{time.strftime('%Y%m%d')}.json"
        filepath = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            on_export(filepath)

    def handle_sort(self, column, on_sort):
        on_sort(column, self.sort_reverse)
        self.update_headings(column, self.sort_reverse, on_sort)
        self.sort_reverse = not self.sort_reverse

    def set_selection(self, index):
        children = self.treeview.get_children()
        if 0 <= index < len(children):
            self.treeview.selection_set(children[index])

    def get_selection(self):
        children = self.treeview.selection()
        if not children:
            return
        return self.treeview.index(children[0])

##--Вікно ігр--##
class GameBoard(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Default empty functions so it doesn't crash if a game doesn't use them
        self.on_click = lambda tags, x, y: None
        self.on_drag = lambda x, y: None
        self.on_release = lambda: None

        self.commands = {
            "oval": self.canvas.create_oval,
            "rectangle": self.canvas.create_rectangle,
            "triangle": lambda x1, y1, x2, y2, **opts: self.canvas.create_polygon(x1, y2, (x1+x2)//2, y1, x2, y2, **opts),
            "star": lambda x1, y1, x2, y2, **opts: self.canvas.create_polygon(x1, (y1+y2)//2, (x1+x2)//2, y1, x2, (y1+y2)//2, (x1+x2)//2, y2, **opts),
            "diamond": lambda x1, y1, x2, y2, **opts: self.canvas.create_polygon((x1+x2)//2, y1, x2, (y1+y2)//2, (x1+x2)//2, y2, x1, (y1+y2)//2, **opts),
            "text": self.canvas.create_text,
        }

        self.canvas.bind("<ButtonPress-1>", self.handle_press)
        self.canvas.bind("<B1-Motion>", lambda e: self.on_drag(e.x, e.y))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.on_release())

    def render(self, shapes):
        self.canvas.delete("all")
        for shape in shapes:
            kind, coords, opts = shape["kind"], shape["coords"], shape["options"]
            if kind in self.commands:
                self.commands[kind](*coords, **opts)

    def handle_press(self, e):
        items = self.canvas.find_overlapping(e.x, e.y, e.x, e.y)
        if items:
            tags = self.canvas.gettags(items[-1])
            self.on_click(tags, e.x, e.y) # Pass ALL tags, making it more flexible
        else:
            self.on_click((), e.x, e.y) # Empty tuple for empty background

##--Вікно із результатами гри--##
class ResultDialog(tk.Toplevel):
    def __init__(self, master, title, message, elapsed, score, lang):
        super().__init__(master)
        self.dialog = None
        self.title(title)
        self.geometry("300x200")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(master)
        self.grab_set()

        # Display Stats
        ttk.Label(self, text=message, font=("Helvetica", 12, "bold"),  anchor="center").pack(pady=10, fill="x")
        ttk.Label(self, text=lang["time"] + f": {elapsed}", font=("Helvetica", 10)).pack()
        ttk.Label(self, text=lang["score"] + f": {score}", font=("Helvetica", 10)).pack()

        # Username Entry
        ttk.Label(self, text=lang["enter_name"], font=("Helvetica", 10)).pack()
        self.entry = ttk.Entry(self)
        self.entry.insert(0, "Player") # Default name
        self.entry.pack(pady=5, padx=20, fill="x")
        self.entry.focus_set()

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text=lang["save_close"], command=self.handle_ok).pack(side="left", padx=5)

        center_window(self, master)

    def handle_ok(self):
        self.dialog = self.entry.get()
        self.destroy()

    def get_result(self):
        self.wait_window() # This is crucial: it pauses code execution until window is closed
        return self.dialog
    
class CustomSettingsWindow(tk.Toplevel):
    def __init__(self, master, current_config, on_save, lang):
        super().__init__(master)
        self.title(lang["customsettingswindow_title"])
        self.geometry("420x600")
        self.on_save = on_save
        self.transient(master)
        self.grab_set()

        # --- Scrollable Canvas Setup ---
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, background="#f0f0f0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # --- 1. General Settings Group ---
        gen_frame = tk.LabelFrame(self.scrollable_frame, text=lang["general_settings"], padx=10, pady=10, font=("Helvetica", 10, "bold"))
        gen_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(gen_frame, text=lang["time_limit_setting"]).pack()
        self.time_var = tk.StringVar(value=str(current_config["time"]))
        ttk.Combobox(gen_frame, textvariable=self.time_var, values=["15", "30", "45", "60", "120"]).pack(pady=2)

        # --- 2. Sorting Game Group ---
        sort_frame = tk.LabelFrame(self.scrollable_frame, text=lang["sorting_game"], padx=10, pady=10, font=("Helvetica", 10, "bold"))
        sort_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(sort_frame, text=lang["basket_number_setting"]).pack()
        self.basket_var = tk.IntVar(value=current_config["baskets"])
        tk.Scale(sort_frame, from_=1, to=5, orient="horizontal", variable=self.basket_var).pack(fill="x")

        ttk.Label(sort_frame, text=lang["sort_items_setting"]).pack()
        self.items_var = tk.IntVar(value=current_config["items"])
        tk.Scale(sort_frame, from_=10, to=30, orient="horizontal", variable=self.items_var).pack(fill="x")

        # --- 3. Aim Trainer Group ---
        aim_frame = tk.LabelFrame(self.scrollable_frame, text=lang["aim_trainer"], padx=10, pady=10, font=("Helvetica", 10, "bold"))
        aim_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(aim_frame, text=lang["target_size_setting"]).pack()
        self.size_var = tk.IntVar(value=current_config["target_size"])
        tk.Scale(aim_frame, from_=10, to=50, orient="horizontal", variable=self.size_var).pack(fill="x")

        # --- 4. Memory Game Group ---
        mem_frame = tk.LabelFrame(self.scrollable_frame, text=lang["memory_match"], padx=10, pady=10, font=("Helvetica", 10, "bold"))
        mem_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(mem_frame, text=lang["sequence_length_setting"]).pack()
        self.mem_var = tk.StringVar(value=str(current_config["memory_items"]))
        self.mem_var.trace_add("write", self.validate_entry)
        self.mem_entry = ttk.Entry(mem_frame, textvariable=self.mem_var, width=10)
        self.mem_entry.pack()
        self.error_label = tk.Label(mem_frame, text="", fg="red", font=("Helvetica", 10))
        self.error_label.pack()

        ttk.Label(mem_frame, text=lang["unique_colors_setting"]).pack()
        self.color_var = tk.IntVar(value=current_config["mem_colors"])
        tk.Spinbox(mem_frame, from_=1, to=7, textvariable=self.color_var, width=10).pack()

        ttk.Label(sort_frame, text=lang["unique_shapes_setting"]).pack()
        self.shape_var = tk.IntVar(value=current_config["mem_shapes"])
        tk.Spinbox(sort_frame, from_=1, to=5, textvariable=self.shape_var, width=10).pack()

        # --- 5. Reaction Game Group ---
        react_frame = tk.LabelFrame(self.scrollable_frame, text=lang["reaction_game"], padx=10, pady=10, font=("Helvetica", 10, "bold"))
        react_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(react_frame, text=lang["stay_time_setting"]).pack()
        self.stay_var = tk.IntVar(value=current_config["stay_time"])
        ttk.Combobox(react_frame, textvariable=self.stay_var, values=[500, 1000, 1500, 2000]).pack()

        ttk.Label(react_frame, text=lang["wait_time_setting"]).pack()
        self.react_base_var = tk.IntVar(value=current_config["reaction_wait"][0])
        tk.Spinbox(react_frame, from_=500, to=5000, increment=250, textvariable=self.react_base_var, width=10).pack()
        self.is_random_var = tk.BooleanVar(value=current_config["reaction_wait"][0] != current_config["reaction_wait"][1])
        ttk.Checkbutton(react_frame, text=lang["random_delay_setting"], variable=self.is_random_var).pack()

        # --- 6. Typing Game Group ---
        type_frame = tk.LabelFrame(self.scrollable_frame, text=lang["typing_game"], padx=10, pady=10, font=("Helvetica", 10, "bold"))
        type_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(type_frame, text=lang["word_count_setting"]).pack()
        self.word_var = tk.IntVar(value=current_config.get("word_count", 5))
        tk.Scale(type_frame, from_=1, to=15, orient="horizontal", variable=self.word_var).pack(fill="x")

        # --- Footer ---
        self.save_btn = ttk.Button(self.scrollable_frame, text=lang["save_close"], command=lambda: self.handle_save(lang))
        self.save_btn.pack(pady=20)

        center_window(self, master)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def validate_entry(self, *args):
        val = self.mem_var.get()
        is_valid = val.isdigit() and 1 <= int(val) <= 10
        self.mem_entry.config(bg="white" if is_valid else "#ffcccc")
        self.save_btn.config(state="normal" if is_valid else "disabled")
        self.error_label.config(text="" if is_valid else "Enter 1-10")

    def handle_save(self, lang):
        try:
            base_wait = self.react_base_var.get()
            wait_range = (base_wait, base_wait + 2000) if self.is_random_var.get() else (base_wait, base_wait)

            new_data = {
                "time": int(self.time_var.get()),
                "baskets": self.basket_var.get(),
                "memory_items": int(self.mem_var.get()),
                "target_size": self.size_var.get(),
                "mem_colors": self.color_var.get(),
                "mem_shapes": self.shape_var.get(), 
                "items": self.items_var.get(),
                "stay_time": self.stay_var.get(),
                "word_count": self.word_var.get(),
                "reaction_wait": wait_range
            }
            self.on_save(new_data)
            self.destroy()
        except Exception:
            self.error_label.config(text=lang["error_input"])

class ViewApp(ttk.Frame):
    def __init__(self, master, lang):
        super().__init__(master)
        self.setup_window(800, 600)
        self.pack(fill="both", expand=True)
        
        self.style_manager = StyleManager(master)
        
        self.create_widgets(lang)
        self.menu_bar = BarMenu(self.master, lang)


    def setup_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")
        self.master.resizable(False, False)

    def rebuild_main_frame(self, lang):
        if hasattr(self, "main_frame"):
            self.main_frame.destroy()
        self.master.title(lang["title"])
        self.create_widgets(lang)

    def create_widgets(self, lang):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.grid(sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)

        # Title
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, pady=10)
        self.lbl_greeting = ttk.Label(title_frame, text=lang["greeting"], style="Title.TLabel")
        self.lbl_greeting.pack()

        # Subtitle
        subtitle = ttk.Label(title_frame, text=lang["choose_game"], font=("Helvetica", 10))
        subtitle.pack()

        # Games grid
        games_frame = ttk.LabelFrame(self.main_frame, text=lang["available_games"], padding="15")
        games_frame.grid(row=1, column=0, pady=20, padx=10, sticky="ew")
        games_frame.columnconfigure((0, 1, 2), weight=1)

        games = [
            ("sorting_game", "DragDrop"),
            ("memory_match", "Memory"),
            ("aim_trainer", "AimTrainer"),
            ("reaction_game", "Reaction"),
            ("typing_game", "Typing")
        ]

        for idx, (name, game_cmd) in enumerate(games):
            btn = ttk.Button(
                games_frame, 
                text=lang[name],
                command=lambda gc=game_cmd:
                    self.menu_bar.handle_command(f"{gc}_{self.selected_difficulty.get()}")
            )
            btn.grid(row=0, column=idx, padx=5, pady=10, sticky="ew", ipadx=15, ipady=15)

        # Difficulty selector
        diff_frame = ttk.LabelFrame(self.main_frame, text=lang["difficulty"], padding="10")
        diff_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        self.selected_difficulty = tk.StringVar(value="Easy")

        difficulties = [
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
            ("custom", "Custom")
        ]

        for idx, (name, game_cmd) in enumerate(difficulties):
            ttk.Radiobutton(
                diff_frame, 
                text=lang[name], 
                variable=self.selected_difficulty, 
                value=game_cmd
            ).pack(side="left", padx=10)

        # Daily goals progress
        goals_frame = ttk.LabelFrame(self.main_frame, text=lang["daily_progress"], padding="10")
        goals_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        self.goal_bars = {}
        for row, (name, key) in enumerate(games):
            ttk.Label(goals_frame, text=lang[name]).grid(row=row,column=0,sticky="w")
            progress = ttk.Progressbar(goals_frame, length=250, maximum=100)
            progress.grid(row=row, column=1, padx=5, pady=3)
            value_label = ttk.Label(goals_frame, text="")
            value_label.grid(row=row, column=2)
            self.goal_bars[key] = {
                "bar": progress,
                "label": value_label
            }

    def update_daily_goals(self, progress_data, goal_data, lang):
        for game, widgets in self.goal_bars.items():
            current = progress_data.get(game, 0)
            maximum = goal_data.get(game, 100)

            widgets["bar"].config(maximum=maximum, value=current)

            text_value = lang["goal_completed"] if current >= maximum else f"{current}/{maximum}"
            widgets["label"].config(text=text_value)

    def prepare_game_layout(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def open_options_window(self, current_lang, lang_list, on_save_callback, lang):
        LanguageWindow(self.master, current_lang, lang_list, on_save_callback, lang)

    def open_history_window(self, history, on_delete, on_export, on_import, on_sort, lang):
        return HistoryWindow(self.master, history, on_delete, on_export, on_import, on_sort, lang)
    
    def open_custom_settings(self, current_config, on_update, lang):
        CustomSettingsWindow(self.master, current_config, on_update, lang)
    
    def display_game_message(self, text, color, width, height):
        if hasattr(self, 'game'):
            self.game.canvas.delete("notification")
            center_x = width / 2
            center_y = height / 5
            self.game.canvas.create_text(
                center_x, center_y,
                text=text, 
                fill=color, 
                font=("Helvetica", 40, "bold"),
                tag="notification"
            )

    def create_game_board(self, lang):
        self.hud_frame = ttk.Frame(self.main_frame)
        self.hud_frame.pack(fill="x", pady=5)
        
        self.lbl_score = ttk.Label(self.hud_frame, text="Score: 0", font=("Helvetica", 12, "bold"))
        self.lbl_score.pack(side="left", padx=20)
        
        self.lbl_time = ttk.Label(self.hud_frame, text="Time: 0s", font=("Helvetica", 12, "bold"))
        self.lbl_time.pack(side="right", padx=20)

        # Create the canvas below it
        self.game = GameBoard(self.main_frame)
        self.game.pack(fill="both", expand=True)
        return self.game
    
    def update_hud(self, score, time_left, lang):
        """Updates the HUD labels with current stats."""
        if hasattr(self, 'lbl_score'):
            self.lbl_score.config(text=lang["score"] + ": " + str(score))
        if hasattr(self, 'lbl_time'):
            # Show red text if time is running low (less than 5 seconds)
            color = "red" if time_left <= 5 else "black"
            self.lbl_time.config( text=lang["time"] + f": {int(time_left)}s", foreground=color)

    def create_result_dialog(self, title, message, elapsed, score, lang):
        dialog = ResultDialog(self.master, title, message, elapsed, score, lang)
        return dialog.get_result()
    
    def show_message_box(self, title, text, box_type):
        boxes = {
            "info": messagebox.showinfo,
            "warning": messagebox.showwarning,
            "error": messagebox.showerror,
            "question": messagebox.askyesno
        }

        return boxes[box_type](title, text)
    

