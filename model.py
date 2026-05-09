import random
import time
import json

class ModelApp:
    def __init__(self):
        ##--Змінні--##
        self.available_languages = ["English", "Українська"]
        self.languages = {
            "English": {
                "title": "Minigame Suite",
                "language": "Language",
                "greeting": "Welcome!",
                "new_game": "New Game", 
                "options": "Options",
                "history": "History",
                "exit": "Exit",
                "sorting_game": "Sorting Game",
                "memory_match": "Memory Match",
                "aim_trainer": "Aim Trainer",
                "reaction_game": "Reaction game",
                "typing_game": "Speedtyping game",
                "time_up": "Time's Up!",
                "victory_msg": "Perfect!",
                "game_over": "Game Over",
                "wrong": "Wrong!",
                "memorize": "Memorize the sequence!",
                "game_in_progress": "Please finish the current game before starting a new one.",
                "error_import": "Failed to import history. Check file format.",
                "success_import": "History imported successfully!",
                "delete_history_confirm": "Are you sure you want to delete this record?",
                "error_export": "Failed to save history file.",
                "success_export": "History saved to: {filepath}",
                "update_custom_difficulty": "Custom difficulty updated!",
                "exit_confirm": "Are you sure you want to exit the game?",
                "exit_game_confirm": "Game in progress. Exit anyway?",
                "language_settings_title": "Language Settings",
                "language_select": "Select your language:",
                "apply": "Apply",
                "import_button": "Import from JSON",
                "export_button": "Export to JSON",
                "delete_button": "Delete",
                "history_window_title": "Game History",
                "user": "User",
                "game": "Game",
                "difficulty": "Difficulty",
                "time": "Time",
                "date": "Date",
                "score": "Score",
                "enter_name": "Enter your name:",
                "save_close": "Save & close",
                "error_input": "Invalid data!",
                "easy": "Easy",
                "medium": "Medium",
                "hard": "Hard",
                "custom": "Custom",
                "view_scores": "View scores",
                "customsettingswindow_title": "Custom difficulty",
                "general_settings": "General settings",
                "time_limit_setting": "Time Limit (seconds)",
                "basket_number_setting": "Number of Baskets (1-5)",
                "sort_items_setting": "Total Items to Sort",
                "target_size_setting": "Target Size (pixels)",
                "sequence_length_setting": "Sequence Length (1-10)",
                "unique_colors_setting": "Amount of unique colors",
                "stay_time_setting": "How long the button stays lit (ms)",
                "wait_time_setting": "Waiting time for button",
                "word_count_setting": "Number of words",
                "random_delay_setting": "Add random delay",
                "choose_game": "Choose a game to play",
                "available_games": "Available games",
                "exit_game_message": "Game exited by user.",
                "daily_progress": "Daily Progress",
                "goal_completed": "Goal completed!"
            },
            "Українська": {
                "title": "Колекція міні-ігор",
                "language": "Мова",
                "greeting": "Ласкаво просимо!",
                "new_game": "Нова гра", 
                "options": "Опції",
                "history": "Історія", 
                "exit": "Вихід",
                "sorting_game": "Гра сортування",
                "memory_match": "Гра на пам'ять",
                "aim_trainer": "Тренажер прицілу",
                "reaction_game": "Гра на реакцію",
                "typing_game": "Гра на швидке друкування",
                "time_up": "Час вийшов!",
                "victory_msg": "Чудово!",
                "game_over": "Гра закінчена",
                "wrong": "Неправильно!",
                "memorize": "Запам'ятайте послідовність!",
                "game_in_progress": "Будь ласка, завершіть поточну гру, перш ніж розпочинати нову.",
                "error_import": "Не вдалося імпортувати історію. Перевірте формат файлу.",
                "success_import": "Історія успішно імпортована!",
                "delete_history_confirm": "Ви впевнені, що хочете видалити цей запис?",
                "error_export": "Не вдалося зберегти файл історії.",
                "success_export": "Історія збережена в: {filepath}",
                "update_custom_difficulty": "Користувацька складність оновлено!",
                "exit_confirm": "Ви впевнені, що хочете вийти з гри?",
                "exit_game_confirm": "Гра триває. Все одно вийти?",
                "language_settings_title": "Налаштування мови",
                "language_select": "Виберіть вашу мову:",
                "apply": "Застосувати",
                "import_button": "Імпортувати з JSON",
                "export_button": "Експортувати у JSON",
                "delete_button": "Видалити",
                "history_window_title": "Історія ігр",
                "user": "Гравець",
                "game": "Гра",
                "difficulty": "Складність",
                "time": "Час",
                "date": "Дата",
                "score": "Рахунок",
                "enter_name": "Введіть своє ім'я:",
                "save_close": "Зберегти та закрити",
                "error_input": "Недійсні дані!",
                "easy": "Легка",
                "medium": "Середня",
                "hard": "Важка",
                "custom": "Користувацька",
                "view_scores": "Переглянути рахунки",
                "customsettingswindow_title": "Користувацька складність",
                "general_settings": "Загальні налаштування",
                "time_limit_setting": "Ліміт часу (секунди)",
                "basket_number_setting": "Кількість кошиків (1-5)",
                "sort_items_setting": "Загальна кількість елементів для сортування",
                "target_size_setting": "Розмір цілі (пікселі)",
                "sequence_length_setting": "Довжина послідовності (1-10)",
                "unique_colors_setting": "Кількість унікальних кольорів",
                "stay_time_setting": "Як довго кнопка світиться (мс)",
                "wait_time_setting": "Час очікування кнопки",
                "word_count_setting": "Кількість слів",
                "random_delay_setting": "Додати випадкову затримку",
                "choose_game": "Виберіть гру у яку грати",
                "available_games": "Доступні ігри",
                "exit_game_message": "Користувач вийшов з гри.",
                "daily_progress": "Щоденний прогрес",
                "goal_completed": "Мета досягнута!"
            }
        }
        
        self.current_lang = "English"
        self.history = self.load_on_startup()
        self.shapes = []
        self.current_game = None
        self.current_difficulty = None
        self.start_time = 0
        self.current_score = 0
        self.daily_progress = {
            "DragDrop": 0,
            "Memory": 0,
            "AimTrainer": 0,
            "Reaction": 0,
            "Typing": 0
        }
        self.daily_goals = {
            "DragDrop": 100,
            "Memory": 50,
            "AimTrainer": 200,
            "Reaction": 30,
            "Typing": 500
        }
        self.current_game_config = None
        self.is_active = False
        self.time_limit = 0
        self.reaction_state = None
        self.memory_step = 0
        self.w = None
        self.h = None
        
        # Game Settings
        self.difficulty_config = {
            "Easy": {"time": 30, "items": 20, "baskets": 1, "target_size": 30, "memory_items": 4, "mem_colors": 3, "mem_shapes": 2, "stay_time": 2000, "reaction_wait": (1000, 3000), "word_count": 3},
            "Medium": {"time": 20, "items": 15, "baskets": 2, "target_size": 20, "memory_items": 6, "mem_colors": 4, "mem_shapes": 3, "stay_time": 1500, "reaction_wait": (700, 2000), "word_count": 5},
            "Hard": {"time": 10, "items": 10, "baskets": 3, "target_size": 10, "memory_items": 8, "mem_colors": 6, "mem_shapes": 5, "stay_time": 1000, "reaction_wait": (500, 1500), "word_count": 8},
            "Custom": {"time": 60, "items": 10, "baskets": 2, "target_size": 25, "memory_items": 4, "mem_colors": 3, "mem_shapes": 2, "stay_time": 1500, "reaction_wait": (500, 2000), "word_count": 5}
        }

        self.notify_game = lambda s: None
        self.notify_history = lambda h: None
        
    ##--Переклад--##
    def translate(self, key):
        return self.languages[self.current_lang].get(key, key)
    
    ##--Гру сортування--##
    def load_sorting_game(self, difficulty):
        self.current_game_config = self.difficulty_config[difficulty]
        colors = ["red", "blue", "green", "purple", "orange"]
    
        num_baskets = self.current_game_config["baskets"]
        game_colors = random.sample(colors, num_baskets)
    
        new_shapes = []

        padding_top = 50
        padding_bottom = 50
        available_h = self.h - padding_top - padding_bottom
        gap = 10
        basket_h = min(90, (available_h // num_baskets) - gap)
        basket_w = 120
    
        for i in range(num_baskets):
            color = game_colors[i]
        
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
        for i in range(self.current_game_config["items"]):
            color = random.choice(game_colors)
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
        self.notify_game(self.shapes)
        
        ##--Тренажер прицілу--##
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
        max_x = max(self.last_w - size - 20, 20)
        max_y = max(self.last_h - size - 20, 20)
        
        x = random.randint(20, max_x)
        y = random.randint(20, max_y)
        
        self.shapes = [{
            "kind": "oval",
            "coords": [x, y, x + size, y + size],
            "options": {"fill": "red", "outline": "white", "tag": ("target", "click")}
        }]
        self.notify_game(self.shapes)

    ##--Гра на пам'ять--##
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
        self.notify_game(self.shapes)

    def scatter_memory_shapes(self):
        self.memory_step = 0 
        
        max_x = max(self.last_w - 70, 30)
        max_y = max(self.last_h - 70, 80)
        for shape in self.shapes:
            x = random.randint(30, max_x)
            y = random.randint(80, max_y) 
            
            shape["coords"] = [x, y, x + 40, y + 40]
            shape["options"]["tag"] = (shape["id"], "memory_click", shape["options"]["fill"], shape["kind"])
            
        random.shuffle(self.shapes) 
        self.notify_game(self.shapes)

    ##--Гра на реакцію--##
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
        self.notify_game(self.shapes)

    ##--Гра на швидке друкування--##
    def load_typing_game(self, difficulty):
        self.current_game_config = self.difficulty_config[difficulty]
        words = ["python", "coding", "interface", "keyboard", "reaction", "velocity", "monitor", "challenge", "program", "developer", "function", "variable", "object", "class", "method", "inheritance", "encapsulation", "polymorphism", "abstraction", "algorithm"]
        # Select words based on difficulty
        count = self.current_game_config["word_count"]
        self.target_text = " ".join(random.sample(words, count))
        self.typed_chars = [] # List of (char, color)
        self.current_char_index = 0
        self.configure_typing_text()

    def configure_typing_text(self):
        self.shapes = []

        char_width = 18
        space_width = char_width 
        line_height = 40
        margin_x = 40
        max_width = self.w - margin_x

        current_x = margin_x
        current_y = self.h // 2 - 40

        char_index = 0 

        words = self.target_text.split(" ")

        for w_i, word in enumerate(words):
            word_width = len(word) * char_width
            if current_x + word_width > max_width:
                current_x = margin_x
                current_y += line_height

            for i, char in enumerate(word):
                color = "gray"

                if char_index < len(self.typed_chars):
                    color = self.typed_chars[char_index][1]
                elif char_index == self.current_char_index:
                    color = "blue"

                self.shapes.append({
                    "kind": "text",
                    "coords": [current_x, current_y],
                    "options": {
                        "text": char,
                        "fill": color,
                        "font": ("Courier", 24, "bold"),
                        "tags": ("typing_text",)
                    }
                })

                current_x += char_width
                char_index += 1

            if w_i != len(words) - 1:
                if current_x + space_width > max_width:
                    current_x = margin_x
                    current_y += line_height

                self.shapes.append({
                    "kind": "text",
                    "coords": [current_x, current_y],
                    "options": {
                        "text": " ",
                        "fill": "gray",
                        "font": ("Courier", 24, "bold"),
                        "tags": ("typing_text",)
                    }
                })

                current_x += space_width
                char_index += 1

        self.notify_game(self.shapes)

    ##--Експорт і імпортування історії--##
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
        
        ##--Завантаження історії, якщо вона є--##
    def load_on_startup(self):
        try:
            with open("autosave_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] 

        ##--Повернення часу, що залишився--##
    def get_remaining_time(self):
        if not self.is_active:
            return 0
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        return remaining
    
    ##--Оновлення очків--##
    def update_score(self, points):
        self.current_score += points

    ##--Методи з історією--##
    def set_history(self, history, index):
        self.history = history
        self.notify_history(self.history, index)

    def get_history(self):
        return self.history.copy()

    def load_history(self):
        history = self.get_history()
        self.set_history(history, 0)

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

    def delete_history(self, index):
        history = self.get_history()
        history.pop(index)
        index = min(index, len(history)-1)
        self.set_history(history, index)

    def sort_history(self, key, reverse=False):
        history = self.get_history()
        if key == "score":
            history.sort(key=lambda r: int(r["score"]), reverse=reverse)
        elif key == "time":
            history.sort(
                key=lambda r: float(str(r["time"]).replace("s", "")),
                reverse=reverse
            )
        else:
            history.sort(key=lambda r: str(r[key]).lower(), reverse=reverse)
        self.set_history(history, 0)

    ##--Методи з прогресами та цілями--##
    def get_progress(self):
        return self.daily_progress.copy()
    
    def set_progress(self, progress):
        self.daily_progress = progress

    def add_progress(self):
        progress = self.get_progress()
        if self.current_game:
            progress[self.current_game] += self.current_score
            self.set_progress(progress)

    def get_goals(self):
        return self.daily_goals.copy()
