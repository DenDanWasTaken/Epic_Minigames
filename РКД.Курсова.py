import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import random
import time
import json

class ModelApp:
    def __init__(self):
        self.available_languages = ["English", "Українська"]
        self.languages = {
            "English": {
                "greeting": "Welcome!",
                "new_game": "New Game", 
                "options": "Options",
                "history": "History",
                "exit": "Exit",
                "sorting_game": "Sorting Game",
                "memory_match": "Memory Match",
                "aim_trainer": "Aim Trainer"
            },
            "Українська": {
                "greeting": "Ласкаво просимо!",
                "new_game": "Нова гра", 
                "options": "Опції",
                "history": "Історія", 
                "exit": "Вихід",
                "sorting_game": "Гра сортування",
                "memory_match": "Гра пам'яті",
                "aim_trainer": "Тренажер меткости"
            }
        }
        self.current_lang = "English"
        self.history = self.load_on_startup()
        self.shapes = []
        self.current_game = None
        self.current_difficulty = None
        self.start_time = 0
        self.current_score = 0
        self.current_game_config = None
        self.is_active = False
        self.time_limit = 0
        self.reaction_state = None
        self.w = None
        self.h = None
        
        # Game Settings
        self.difficulty_config = {
            "Easy": {"time": 30, "items": 20, "baskets": 1, "target_size": 30, "memory_items": 3, "mem_colors": 2, "mem_shapes": 1, "stay_time": 2000, "reaction_wait": (1000, 3000), "word_count": 3},
            "Medium": {"time": 20, "items": 15, "baskets": 2, "target_size": 20, "memory_items": 5, "mem_colors": 4, "mem_shapes": 2, "stay_time": 1500, "reaction_wait": (700, 2000), "word_count": 5},
            "Hard": {"time": 10, "items": 10, "baskets": 3, "target_size": 10, "memory_items": 7, "mem_colors": 6, "mem_shapes": 3, "stay_time": 1000, "reaction_wait": (500, 1500), "word_count": 8},
            "Custom": {"time": 60, "items": 10, "baskets": 2, "target_size": 25, "memory_items": 4, "mem_colors": 3, "mem_shapes": 2, "stay_time": 1500, "reaction_wait": (500, 2000), "word_count": 5}
        }

        self.notify = lambda s: None

    def save_record(self, username, game_name, difficulty, time_spent, score):
        record = {
            "user": username or "Anonymous", # Fallback if empty
            "game": game_name,
            "difficulty": difficulty,
            "time": f"{time_spent}s",
            "score": score,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(record)
        print(f"Record Saved: {record}")
        self.export_history("autosave_history.json")

    def load_sorting_game(self, difficulty):
        self.current_game_config = self.difficulty_config[difficulty]
        colors = ["red", "blue", "green", "purple", "orange"]
    
        num_baskets = self.current_game_config["baskets"]
        game_colors = random.sample(colors, num_baskets)
    
        new_shapes = []

    # --- DYNAMIC BASKET CALCULATION ---
    # We want baskets on the right side. 
    # basket_h: Divide available height by number of baskets, capped at 90px
        padding_top = 50
        padding_bottom = 50
        available_h = self.h - padding_top - padding_bottom
        gap = 10
    
    # This prevents the baskets from overlapping or going out of bounds
        basket_h = min(90, (available_h // num_baskets) - gap)
        basket_w = 120
    
    # 1. Create Baskets
        for i in range(num_baskets):
            color = game_colors[i]
        
        # Position 20px from the right edge
            x1 = self.w - basket_w - 20
            y1 = padding_top + (i * (basket_h + gap))
        
            new_shapes.append({
                "kind": "rectangle", 
                "coords": [x1, y1, x1 + basket_w, y1 + basket_h],
                "options": {
                    "fill": color, "stipple": "gray50",
                    "outline": "black", "width": 2,
                    "tag": (f"basket_{color}", "target", color)
                }
            })

    # --- DYNAMIC ITEM SPAWNING ---
    # 2. Create Trash Items (Balls)
        for i in range(self.current_game_config["items"]):
            color = random.choice(game_colors)
        
        # Spawn items ONLY in the left 60% of the screen so they don't start on top of baskets
        # spawn_w_limit = int(w * 0.6)
            x = random.randint(20, int(self.w * 0.6) - 40)
            y = random.randint(padding_top, self.h - 60)
        
            new_shapes.append({
                "kind": "oval", 
                "coords": [x, y, x + 40, y + 40],
                "options": {
                    "fill": color, "outline": "white", 
                    "tag": (f"item_{i}", "drag", color)
                }
            })
    
        self.shapes = new_shapes
        self.notify(self.shapes)
        
    def load_aim_trainer(self, level):
        self.current_game_config = self.difficulty_config[level]
        # We store w and h so the model can generate new targets 
        # without needing the controller to pass them every single click
        self.last_w, self.last_h = self.w, self.h 
        self.generate_new_target()

    def generate_new_target(self):
        self.shapes = []
        size = self.current_game_config["target_size"]
        
        # Calculate safe spawn range
        # We subtract 'size' to ensure the right/bottom edge stays inside
        max_x = self.last_w - size - 20
        max_y = self.last_h - size - 20
        
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
        
        self.shapes = [{
            "kind": "oval",
            "coords": [x, y, x + size, y + size],
            "options": {"fill": "red", "outline": "white", "tag": ("target", "click")}
        }]
        self.notify(self.shapes)

    def load_memory_game(self, difficulty):
        self.current_game_config = self.difficulty_config[difficulty]
        self.last_w, self.last_h = self.w, self.h # Store for scattering later

        all_colors = ["red", "blue", "green", "purple", "orange", "yellow", "cyan", "magenta", "lime", "pink"]
        all_kinds = ["oval", "rectangle", "triangle", "star", "diamond"]
        
        available_colors = all_colors[:self.current_game_config["mem_colors"]]
        available_kinds = all_kinds[:self.current_game_config["mem_shapes"]]
        
        self.memory_sequence = []
        num_items = self.current_game_config["memory_items"]
        
        # --- DYNAMIC CENTERING ---
        item_size = 40
        gap = 20
        total_width = (num_items * item_size) + ((num_items - 1) * gap)
        start_x = (self.w - total_width) // 2 
        
        for i in range(num_items):
            color = random.choice(available_colors)
            kind = random.choice(available_kinds)
            
            x1 = start_x + (i * (item_size + gap))
            y1 = self.h // 2 - 20 # Center vertically
            
            shape_data = {
                "id": f"mem_{i}",
                "kind": kind,
                "coords": [x1, y1, x1 + item_size, y1 + item_size],
                "options": {
                    "fill": color, "outline": "black", "width": 2, 
                    "tag": (f"mem_{i}", "memorize", color, kind)
                }
            }
            self.memory_sequence.append(shape_data)
        
        self.shapes = [dict(s) for s in self.memory_sequence]
        self.notify(self.shapes)

    def scatter_memory_shapes(self):
        self.memory_step = 0 
        
        for shape in self.shapes:
            # Randomize within the full dynamic width/height
            # Leave 50px padding for UI labels (Score/Time)
            x = random.randint(30, self.last_w - 70)
            y = random.randint(80, self.last_h - 70) 
            
            shape["coords"] = [x, y, x + 40, y + 40]
            shape["options"]["tag"] = (shape["id"], "memory_click", shape["options"]["fill"], shape["kind"])
            
        random.shuffle(self.shapes) 
        self.notify(self.shapes)

    def load_reaction_game(self, difficulty):
        self.reaction_state = "waiting" # waiting, ready, or clicked
        self.shapes = []
        self.draw_reaction_box("red")

    def draw_reaction_box(self, color):
        size = 200
        x1, y1 = (self.w - size) // 2, (self.h - size) // 2
        self.shapes = [{
            "kind": "rectangle",
            "coords": [x1, y1, x1 + size, y1 + size],
            "options": {"fill": color, "outline": "black", "width": 5, "tags": ("reaction_target", color)}
        }]
        self.notify(self.shapes)

    def load_typing_game(self, difficulty):
        words = ["python", "coding", "interface", "keyboard", "reaction", "velocity", "monitor", "challenge", "program", "developer", "function", "variable", "object", "class", "method", "inheritance", "encapsulation", "polymorphism", "abstraction", "algorithm"]
        # Select words based on difficulty
        count = self.current_game_config["word_count"]
        self.target_text = " ".join(random.sample(words, count))
        self.typed_chars = [] # List of (char, color)
        self.current_char_index = 0
        self.render_typing_text()

    def render_typing_text(self):
        self.shapes = []
        start_x = 50
        char_width = 18
        line_height = 40
        margin_x = 40
        max_width = self.w - margin_x

        current_x = margin_x
        current_y = self.h // 2 - 40 # Starting height
        
        for i, char in enumerate(self.target_text):
            if current_x + char_width > max_width:
                current_x = margin_x  # Reset X to the left margin
                current_y += line_height  # Move Y down
            # Determine color: Gray (untyped), Green (correct), Red (wrong)
            color = "gray"
            if i < len(self.typed_chars):
                color = self.typed_chars[i][1]
            elif i == self.current_char_index:
                color = "blue" # Highlight current letter
            
            self.shapes.append({
                "kind": "text",
                "coords": [start_x + (i * char_width), self.h // 2],
                "options": {
                    "text": char, "fill": color, 
                    "font": ("Courier", 24, "bold"), "tags": ("typing_text",)
                }
            })
            current_x += char_width
        self.notify(self.shapes)

    def export_history(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # indent=4 makes the file human-readable
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
        
    def import_history(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
                if isinstance(new_data, list):
                    self.history.extend(new_data)
                # Optional: Sort history by date after import
                # self.history.sort(key=lambda x: x['date'], reverse=True)
                    return True
        except Exception as e:
            print(f"Error importing history: {e}")
            return False
        return False
        
    def load_on_startup(self):
        try:
            with open("autosave_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return [] # Start fresh if no file exists
        
    def get_remaining_time(self):
        if not self.is_active:
            return 0
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        return remaining
    
    def update_score(self, points):
        self.current_score += points


class BarMenu(tk.Menu):
    def __init__(self, master):
        super().__init__(master)
        master.config(menu=self)
        self.on_menu = lambda cmd: None 
        
        # Main Cascades
        self.game_menu = tk.Menu(self, tearoff=0)
        self.opt_menu = tk.Menu(self, tearoff=0)
        self.hist_menu = tk.Menu(self, tearoff=0)

        self.add_cascade(label="Game", menu=self.game_menu)
        self.add_cascade(label="Options", menu=self.opt_menu)
        self.add_cascade(label="History", menu=self.hist_menu)
        self.add_command(label="Exit", command=lambda: self.handle_command("Exit"))

        self.setup_game_submenus()

        # Other Menu Items
        self.opt_menu.add_command(label="Language", command=lambda: self.handle_command("Language"))
        self.opt_menu.add_command(label="Custom Difficulty", command=lambda: self.handle_command("Custom Difficulty"))
        self.hist_menu.add_command(label="View Scores", command=lambda: self.handle_command("History"))

    def setup_game_submenus(self):
        games = [
            ("Sorting Game", "DragDrop"),
            ("Memory Match", "Memory"),
            ("Aim trainer", "AimTrainer"),
            ("Reaction Test", "Reaction"),
            ("Typing Test", "Typing")
        ]
        
        difficulties = ["Easy", "Medium", "Hard", "Custom"]

        for game_name, game_id in games:
            # Create a submenu for each game
            sub_menu = tk.Menu(self.game_menu, tearoff=0)
            self.game_menu.add_cascade(label=game_name, menu=sub_menu)
            
            for difficulty in difficulties:
                sub_menu.add_command(
                    label=difficulty, 
                    command=lambda g=game_id, d=difficulty: self.handle_command(f"{g}_{d}")
                )

    def handle_command(self, command):
        if self.on_menu:
            self.on_menu(command)

    def update_labels(self, lang_data):
        self.entryconfig(1, label=lang_data["new_game"])
        self.entryconfig(2, label=lang_data["options"])
        self.entryconfig(3, label=lang_data["history"])
        self.entryconfig(5, label=lang_data["exit"])
        self.game_menu.entryconfig(0, label=lang_data["sorting_game"])
        self.game_menu.entryconfig(1, label=lang_data["memory_match"])
        self.game_menu.entryconfig(2, label=lang_data["aim_trainer"])
        
class LanguageWindow(tk.Toplevel):
    def __init__(self, master, current_lang, lang_list, on_save):
        super().__init__(master)
        self.title("Language Settings")
        self.geometry("300x250")
        
        self.transient(master)
        self.grab_set() # Requirement 9: Makes it a proper custom dialog
        
        # Requirement 6: Using labels and radiobuttons
        tk.Label(self, text="Select Language:", font=("Helvetica", 10, "bold")).pack(pady=10)
        
        self.lang_var = tk.StringVar(value=current_lang)
        
        for lang in lang_list:
            ttk.Radiobutton(self, text=lang, variable=self.lang_var, value=lang).pack(anchor="w", padx=50)

        # Requirement 2: Button reaction
        ttk.Button(self, text="Apply", 
                   command=lambda: self.handle_command(on_save)).pack(pady=20)

    def handle_command(self, on_save):
        on_save(self.lang_var.get())
        self.destroy()

class HistoryWindow(tk.Toplevel):
    def __init__(self, master, history, on_export, on_import):
        super().__init__(master)
        self.title("Game History")
        self.geometry("700x400")
        
        self.transient(master)
        self.grab_set() # Makes it a proper custom dialog

        columns = ( "user","game", "difficulty", "time", "date", "score")
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")
        scrollbar.config(command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        self.treeview.pack(side="left", fill="both", expand=True)

        self.treeview.configure(yscrollcommand=scrollbar.set)

        column_widths = {"user": 80, "game": 100, "difficulty": 80, "time": 60, "date": 120, "score": 60}

        for col in columns:
            self.treeview.heading(col, text=col.capitalize())
            self.treeview.column(col, width=column_widths.get(col, 100), anchor="center", stretch=True)

        for record in history:
            self.treeview.insert("", "end", values=(record["user"], record["game"], record["difficulty"], record["time"], record["date"], record["score"]))

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        # Import Button
        ttk.Button(
            btn_frame, 
            text="Import JSON", 
            command=lambda: self.prompt_import(on_import)
        ).pack(side="left", padx=20)

        # Export Button
        ttk.Button(
            btn_frame, 
            text="Export to JSON", 
            command=lambda: self.prompt_export(on_export)
        ).pack(side="right", padx=20)

    def refresh_table(self, history):
        # Clear existing items
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        # Insert history
        for record in history:
            self.treeview.insert("", "end", values=(
                record["user"], record["game"], record["difficulty"], 
                record["time"], record["date"], record["score"]
            ))

    def prompt_import(self, on_import):
        filepath = filedialog.askopenfilename(
            title="Select History File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            # The controller will handle the import and return the updated history
            updated_history = on_import(filepath)
            if updated_history is not None:
                self.refresh_table(updated_history)

    def prompt_export(self, on_export):
        default_name = f"game_history_{time.strftime('%Y%m%d')}.json"
        filepath = filedialog.asksaveasfilename(
            title="Save History",
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            on_export(filepath)

class GameBoard(tk.Frame):
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

class ResultDialog(tk.Toplevel):
    def __init__(self, master, title, message, elapsed, score):
        super().__init__(master)
        self.dialog = None
        self.title(title)
        self.geometry("300x250")
        
        # Make it modal
        self.transient(master)
        self.grab_set()

        # Display Stats
        tk.Label(self, text=message, font=("Helvetica", 12, "bold"), pady=10).pack()
        tk.Label(self, text=f"Time: {elapsed}s", font=("Helvetica", 10)).pack()
        tk.Label(self, text=f"Score: {score}", font=("Helvetica", 10)).pack()

        # Username Entry
        tk.Label(self, text="\nEnter your name:", font=("Helvetica", 10)).pack()
        self.entry = ttk.Entry(self)
        self.entry.insert(0, "Player") # Default name
        self.entry.pack(pady=5, padx=20, fill="x")
        self.entry.focus_set()

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Save & Close", command=self.handle_ok).pack(side="left", padx=5)

    def handle_ok(self):
        self.dialog = self.entry.get()
        self.destroy()

    def get_result(self):
        self.wait_window() # This is crucial: it pauses code execution until window is closed
        return self.dialog
    
class CustomSettingsWindow(tk.Toplevel):
    def __init__(self, master, current_config, on_save):
        super().__init__(master)
        self.title("Custom Difficulty")
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
        gen_frame = tk.LabelFrame(self.scrollable_frame, text=" General Settings ", padx=10, pady=10, font=("Arial", 10, "bold"))
        gen_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(gen_frame, text="Time Limit (seconds):").pack()
        self.time_var = tk.StringVar(value=str(current_config["time"]))
        ttk.Combobox(gen_frame, textvariable=self.time_var, values=["15", "30", "45", "60", "120"]).pack(pady=2)

        # --- 2. Sorting Game Group ---
        sort_frame = tk.LabelFrame(self.scrollable_frame, text=" Sorting Game ", padx=10, pady=10, font=("Arial", 10, "bold"))
        sort_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(sort_frame, text="Number of Baskets (1-5):").pack()
        self.basket_var = tk.IntVar(value=current_config["baskets"])
        tk.Scale(sort_frame, from_=1, to=5, orient="horizontal", variable=self.basket_var).pack(fill="x")

        tk.Label(sort_frame, text="Total Items to Sort:").pack()
        self.items_var = tk.IntVar(value=current_config["items"])
        tk.Scale(sort_frame, from_=10, to=30, orient="horizontal", variable=self.items_var).pack(fill="x")

        # --- 3. Aim Trainer Group ---
        aim_frame = tk.LabelFrame(self.scrollable_frame, text=" Aim Trainer ", padx=10, pady=10, font=("Arial", 10, "bold"))
        aim_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(aim_frame, text="Target Size (pixels):").pack()
        self.size_var = tk.IntVar(value=current_config["target_size"])
        tk.Scale(aim_frame, from_=10, to=50, orient="horizontal", variable=self.size_var).pack(fill="x")

        # --- 4. Memory Game Group ---
        mem_frame = tk.LabelFrame(self.scrollable_frame, text=" Memory Game ", padx=10, pady=10, font=("Arial", 10, "bold"))
        mem_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(mem_frame, text="Sequence Length (1-10):").pack()
        self.mem_var = tk.StringVar(value=str(current_config["memory_items"]))
        self.mem_var.trace_add("write", self.validate_entry)
        self.mem_entry = tk.Entry(mem_frame, textvariable=self.mem_var, width=10)
        self.mem_entry.pack()
        self.error_label = tk.Label(mem_frame, text="", fg="red", font=("Arial", 8))
        self.error_label.pack()

        tk.Label(mem_frame, text="Unique Colors:").pack()
        self.color_var = tk.IntVar(value=current_config["mem_colors"])
        tk.Spinbox(mem_frame, from_=1, to=7, textvariable=self.color_var, width=10).pack()

        # --- 5. Reaction Game Group ---
        react_frame = tk.LabelFrame(self.scrollable_frame, text=" Reaction Test ", padx=10, pady=10, font=("Arial", 10, "bold"))
        react_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(react_frame, text="Stay Time (ms):").pack()
        self.stay_var = tk.IntVar(value=current_config["stay_time"])
        ttk.Combobox(react_frame, textvariable=self.stay_var, values=[500, 1000, 1500, 2000]).pack()

        tk.Label(react_frame, text="Wait Time (ms):").pack()
        self.react_base_var = tk.IntVar(value=current_config["reaction_wait"][0])
        tk.Spinbox(react_frame, from_=500, to=5000, increment=250, textvariable=self.react_base_var, width=10).pack()
        self.is_random_var = tk.BooleanVar(value=current_config["reaction_wait"][0] != current_config["reaction_wait"][1])
        tk.Checkbutton(react_frame, text="Add Random Delay", variable=self.is_random_var).pack()

        # --- 6. Typing Game Group ---
        type_frame = tk.LabelFrame(self.scrollable_frame, text=" Typing Test ", padx=10, pady=10, font=("Arial", 10, "bold"))
        type_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(type_frame, text="Number of Words:").pack()
        self.word_var = tk.IntVar(value=current_config.get("word_count", 5))
        tk.Scale(type_frame, from_=1, to=15, orient="horizontal", variable=self.word_var).pack(fill="x")

        # --- Footer ---
        self.save_btn = ttk.Button(self.scrollable_frame, text="Save & Apply", command=self.handle_save)
        self.save_btn.pack(pady=20)

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

    def handle_save(self):
        try:
            base_wait = self.react_base_var.get()
            wait_range = (base_wait, base_wait + 2000) if self.is_random_var.get() else (base_wait, base_wait)

            new_data = {
                "time": int(self.time_var.get()),
                "baskets": self.basket_var.get(),
                "memory_items": int(self.mem_var.get()),
                "target_size": self.size_var.get(),
                "mem_colors": self.color_var.get(),
                "mem_shapes": 2, # Defaulting minor values
                "items": self.items_var.get(),
                "stay_time": self.stay_var.get(),
                "word_count": self.word_var.get(),
                "reaction_wait": wait_range
            }
            self.on_save(new_data)
            self.destroy()
        except Exception:
            self.error_label.config(text="Invalid data!")

class ViewApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.setup_window(800, 600)
        self.pack(fill="both", expand=True)
        
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 14), padding=10)
        
        self.create_widgets()
        self.menu_bar = BarMenu(self.master)

    def setup_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")
        self.master.resizable(False, False)

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.grid(sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)

        self.lbl_greeting = ttk.Label(self.main_frame, text="")
        self.lbl_greeting.grid(row=0, column=0, pady=20)

    def prepare_game_layout(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def update_ui_text(self, lang_data):
        self.lbl_greeting.config(text=lang_data["greeting"])
        self.menu_bar.update_labels(lang_data)

    def open_options_window(self, current_lang, lang_list, on_save_callback):
        LanguageWindow(self.master, current_lang, lang_list, on_save_callback)

    def open_history_window(self, history, on_export, on_import):
        HistoryWindow(self.master, history, on_export, on_import)
    
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

    def create_game_board(self):
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
    
    def update_hud(self, score, time_left):
        """Updates the HUD labels with current stats."""
        if hasattr(self, 'lbl_score'):
            self.lbl_score.config(text=f"Score: {score}")
        if hasattr(self, 'lbl_time'):
            # Show red text if time is running low (less than 5 seconds)
            color = "red" if time_left <= 5 else "black"
            self.lbl_time.config(text=f"Time: {int(time_left)}s", foreground=color)

    def create_result_dialog(self, title, message, elapsed, score):
        dialog = ResultDialog(self.master, title, message, elapsed, score)
        return dialog.get_result()
    
    def open_custom_settings(self, current_config, on_update):
        CustomSettingsWindow(self.master, current_config, on_update)

class ControllerApp:
    def __init__(self, root):
        self.root = root
        self.model = ModelApp()
        self.view = ViewApp(root)
        self.view.menu_bar.on_menu = self.handle_menu

        self.target = None
        self.model.is_active = False
        self.timer_id = None
        self.refresh_language()

    def handle_menu(self, menu_type):
        print(f"Menu selected: {menu_type}")
        if "_" in menu_type:
        # Split "DragDrop_Easy" into ["DragDrop", "Easy"]
            game_id, difficulty = menu_type.split("_")
            self.model.current_game, self.model.current_difficulty = game_id, difficulty
            self.launch_game(game_id, difficulty)
            return
        actions = {
            "Language": lambda: self.view.open_options_window(self.model.current_lang, self.model.available_languages, self.change_language),
            "History": lambda: self.view.open_history_window(self.model.history, self.save_history_to_file, self.import_history_from_file),
            "Custom Difficulty": lambda: self.view.open_custom_settings(self.model.difficulty_config["Custom"], self.update_custom_difficulty),
            "Exit": self.handle_exit
        }
        action = actions.get(menu_type)
        if action:
            action()

    def handle_exit(self):
        if self.model.is_active:
            if messagebox.askyesno("Exit", "Game in progress. Exit anyway?"):
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
                self.model.is_active = False
                self.show_results("Game exited by user.")
        elif messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def update_custom_difficulty(self, new_config):
        self.model.difficulty_config["Custom"] = new_config
        messagebox.showinfo("Settings", "Custom difficulty updated!")

    def save_history_to_file(self, filepath):
        success = self.model.export_history(filepath)
        if success:
            messagebox.showinfo("Success", f"History saved to:\n{filepath}")
        else:
            messagebox.showerror("Error", "Failed to save history file.")

    def import_history_from_file(self, filepath):
        success = self.model.import_history(filepath)
        if success:
            messagebox.showinfo("Success", "History imported successfully!")
            return self.model.history # Return the list to the View for refreshing
        else:
            messagebox.showerror("Error", "Failed to import history. Check file format.")
            return None

    def change_language(self, new_lang):
        self.model.current_lang = new_lang
        self.refresh_language()

    def refresh_language(self):
        data = self.model.languages[self.model.current_lang]
        self.view.update_ui_text(data)

    def launch_game(self, game_id, difficulty):
        if self.model.is_active:
            messagebox.showwarning("Game in Progress", "Please finish the current game before starting a new one.")
            return
        self.model.is_active = True
        self.view.prepare_game_layout()
        config = self.model.difficulty_config[difficulty]
        self.model.time_limit = config["time"]
        self.model.start_time = time.time()
        self.current_game = self.view.create_game_board()
        self.root.update_idletasks()
        self.model.notify = self.current_game.render
        self.model.w, self.model.h = self.current_game.canvas.winfo_width(), self.current_game.canvas.winfo_height()
        game_map = {
            "DragDrop": self._setup_drag_drop,
            "AimTrainer": self._setup_aim_trainer,
            "Memory": self._setup_memory,
            "Reaction": self._setup_reaction,
            "Typing": self._setup_typing
        }

        setup_func = game_map.get(game_id)
        if setup_func:
            setup_func(difficulty)
            if game_id != "Memory": # Memory handles its own timer start
                self.check_time()

    def _setup_drag_drop(self, diff):
        self.current_game.on_click = self.start_drag
        self.current_game.on_drag = self.drag
        self.current_game.on_release = self.finish_drag
        self.model.load_sorting_game(diff)

    def _setup_aim_trainer(self, diff):
        self.current_game.on_click = self.handle_aim_click
        self.model.load_aim_trainer(diff)

    def _setup_memory(self, diff):
        self.current_game.on_click = self.handle_memory_click
        self.model.load_memory_game(diff)
        self.view.display_game_message("MEMORIZE!", "blue", self.model.w, self.model.h)
        self.root.after(3000, self.begin_memory_recall)

    def _setup_reaction(self, diff):
        self.current_game.on_click = self.handle_reaction_click
        self.model.load_reaction_game(diff)
        self.check_time()
        self.trigger_reaction_timer()

    def _setup_typing(self, diff):
        self.model.load_typing_game(diff)
        self.root.bind("<Key>", self.handle_typing_input)
        self.check_time()

    def trigger_reaction_timer(self):
        if not self.model.is_active or self.model.current_game != "Reaction": 
            return
        # Random delay between 2 and 5 seconds
        delay = random.randint(self.model.difficulty_config[self.model.current_difficulty]["reaction_wait"][0], self.model.difficulty_config[self.model.current_difficulty]["reaction_wait"][1])
        self.root.after(delay, self.make_box_green)

    def make_box_green(self):
        if not self.model.is_active: 
            return
        self.model.reaction_state = "ready"
        self.model.draw_reaction_box("green")
        # How long it stays green depends on difficulty
        stay_time = self.model.difficulty_config[self.model.current_difficulty]["stay_time"]
        self.root.after(stay_time, self.reset_reaction_to_red)

    def reset_reaction_to_red(self):
        if self.model.reaction_state == "ready": # User missed it!
            self.handle_score(-10)
            self.model.reaction_state = "waiting"
            self.model.draw_reaction_box("red")
            self.trigger_reaction_timer()

    def handle_reaction_click(self, tags, x, y):
        if not self.model.is_active:
            return
        if "reaction_target" in tags:
            if "green" in tags:
                self.handle_score(20)
                self.model.reaction_state = "clicked" # Prevent double scoring
                self.model.draw_reaction_box("red")
                self.trigger_reaction_timer()
            else:
                self.handle_score(-5) # Clicked while red

    def handle_typing_input(self, event):
        if not self.model.is_active or len(event.char) != 1: 
            return
        
        target_char = self.model.target_text[self.model.current_char_index]
        if event.char == target_char:
            self.model.typed_chars.append((event.char, "green"))
            self.handle_score(2)
        else:
            self.model.typed_chars.append((event.char, "red"))
            self.handle_score(-1)
        
        self.model.current_char_index += 1
        self.model.render_typing_text()
        
        if self.model.current_char_index >= len(self.model.target_text):
            self.end_game("Text completed!", "blue")

    def check_time(self):
        if not self.model.is_active: 
            return
        
        time_left = self.model.get_remaining_time()
        
        # Update the HUD timer every 100ms
        self.view.update_hud(self.model.current_score, time_left)

        if time_left <= 0:
            self.end_game("Time's up!", "red")
        else:
            self.timer_id = self.root.after(100, self.check_time)

    def handle_aim_click(self, tags, x, y):
        if not self.model.is_active:
            return
        if "target" in tags:
            self.handle_score(1) 
            self.model.generate_new_target() 
        elif not tags: # empty tuple means clicked background
            self.handle_score(-1)

    def start_drag(self, tags, x, y):
        if not self.model.is_active:
            return
        if "drag" in tags:
            # Find the specific item that was clicked using its unique tag
            unique_tag = tags[0]  # e.g., "item_0"
            self.target = self.current_game.canvas.find_withtag(unique_tag)[0]
            self.x, self.y = x, y

    def drag(self, x, y):
        if not self.target: 
            return
        dx, dy = x - self.x, y - self.y
        # Access the canvas inside the current_game instance
        self.current_game.canvas.move(self.target, dx, dy)
        self.x, self.y = x, y

    def finish_drag(self):
        if not self.target: 
            return
        canvas = self.current_game.canvas
        item_tags = canvas.gettags(self.target) # e.g., ("item_1", "drag", "red")
        item_color = item_tags[2]
        
        item_bbox = canvas.bbox(self.target)
        targets = canvas.find_withtag("target")
        
        for t in targets:
            t_bbox = canvas.bbox(t)
            t_tags = canvas.gettags(t) # e.g., ("basket_red", "target", "red")
            basket_color = t_tags[2]

            if self.is_overlapping(item_bbox, t_bbox):
                if item_color == basket_color:
                    canvas.delete(self.target)
                    self.handle_score(10) # 10 points for correct sort
                    
                    # Check if all items are sorted
                    if not canvas.find_withtag("drag"):
                        self.end_game("Perfect!", "green")
                else:
                    # Wrong basket! Bounce the item back slightly
                    canvas.move(self.target, -50, 0)
                    self.handle_score(-5) # Penalty for wrong basket
                break 
                
        self.target = None

    def handle_score(self, points):
        self.model.update_score(points)
        # Update the UI immediately
        elapsed = time.time() - self.model.start_time
        remaining = max(0, self.model.time_limit - elapsed)
        self.view.update_hud(self.model.current_score, remaining)

    def is_overlapping(self, a, b):
        return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
    
    def begin_memory_recall(self):
        if not self.model.is_active: 
            return # Stop if they clicked Exit during the 3 seconds
        
        self.current_game.canvas.delete("notification") # Clear "MEMORIZE!" text
        self.model.scatter_memory_shapes()
        
        # Start the actual timer NOW, so they don't lose time while memorizing
        self.model.start_time = time.time()
        self.check_time()

    def handle_memory_click(self, tags, x, y):
        if not self.model.is_active:
            return
        if "memory_click" in tags:
            # 1. Get the properties of the next item in the sequence
            expected_item = self.model.memory_sequence[self.model.memory_step]
            expected_color = expected_item["options"]["fill"]
            expected_kind = expected_item["kind"]

            # 2. Get the properties of what the user actually clicked
            # We find the item ID using the unique tag (e.g., "mem_4")
            clicked_item_id = self.current_game.canvas.find_withtag(tags[0])[0]
            clicked_color = tags[2]
            clicked_kind = tags[3]
            
            if clicked_color == expected_color and clicked_kind == expected_kind:
                # SUCCESS: Visually identical, so it counts!
                self.handle_score(5)
                self.model.memory_step += 1
                self.current_game.canvas.delete(clicked_item_id)
                
                if self.model.memory_step >= len(self.model.memory_sequence):
                    self.end_game("Perfect", "green")
            else:
                # WRONG
                self.handle_score(-2)
                self.view.display_game_message("WRONG!", "red", self.model.w, self.model.h)
                self.root.after(500, lambda: self.current_game.canvas.delete("notification"))
    
    # Inside ControllerApp
    def end_game(self, message, color):
        if not self.model.is_active:
            return
        self.model.is_active = False
        self.root.unbind("<Key>")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.view.display_game_message(message, color, self.model.w, self.model.h)
        self.root.after(2000, lambda: self.show_results(message))
        
    def show_results(self, message):
        end_time = time.time()
        elapsed = round(end_time - self.model.start_time, 2)
        score = self.model.current_score
        # 1. Show the custom dialog
        username = self.view.create_result_dialog("Game Over", message, elapsed, score)
        # 3. Save the record with the username
        self.model.save_record(
            username,
            self.model.current_game, 
            self.model.current_difficulty, 
            elapsed, 
            score
        )
        self.view.main_frame.destroy()
        self.current_game = None
        self.view.create_widgets()
        self.refresh_language()
        self.model.current_score = 0

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Minigame Suite")
    app = ControllerApp(root)
    root.mainloop()