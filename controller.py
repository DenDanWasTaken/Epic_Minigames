import random
import time
from model import ModelApp
from view import ViewApp

class ControllerApp:
    def __init__(self, root):
        self.root = root
        self.model = ModelApp()
        self.view = ViewApp(root, self.model.languages[self.model.current_lang])
        self.view.menu_bar.on_menu = self.handle_menu

        self.target = None
        self.model.is_active = False
        self.timer_id = None
        self.refresh_language()

    def handle_menu(self, menu_type):
        print(f"Menu selected: {menu_type}")
        if "_" in menu_type:
            # Split "DragDrop_Easy" into ["DragDrop", "Easy"]
            parts = menu_type.split("_", 1)
            if len(parts) == 2:
                game_id, difficulty = parts
                self.model.current_game, self.model.current_difficulty = game_id, difficulty
                self.launch_game(game_id, difficulty)
                return
        actions = {
            "Language": lambda: self.view.open_options_window(self.model.current_lang, self.model.available_languages, self.change_language, self.model.languages[self.model.current_lang]),
            "History": lambda: self.configure_history_window(self.model.history, self.delete_selection, self.save_history_to_file, self.import_history_from_file, self.model.sort_history ,self.model.languages[self.model.current_lang]),
            "Custom Difficulty": lambda: self.view.open_custom_settings(self.model.difficulty_config["Custom"], self.update_custom_difficulty, self.model.languages[self.model.current_lang]),
            "Exit": self.handle_exit
        }
        action = actions.get(menu_type)
        if action:
            action()

    def configure_history_window(self, history, on_delete, on_export, on_import, on_sort, lang):
        history_window = self.view.open_history_window(history, on_delete, on_export, on_import, on_sort, lang)
        self.model.notify_history = history_window.render

    def handle_exit(self):
        if self.model.is_active:
            if self.view.show_message_box(self.model.translate("exit"), self.model.translate("exit_game_confirm"), "question"):
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
                self.model.is_active = False
                self.show_results(self.model.translate("exit_game_message"))
        elif self.view.show_message_box(self.model.translate("exit"), self.model.translate("exit_confirm"), "question"):
            self.root.destroy()

    def update_custom_difficulty(self, new_config):
        self.model.difficulty_config["Custom"] = new_config
        self.view.show_message_box("Settings", self.model.translate("update_custom_difficulty"), "info")

    def save_history_to_file(self, filepath):
        success = self.model.export_history(filepath)
        if success:
            self.view.show_message_box("Success", self.model.translate("success_export").format(filepath=filepath), "info")
        else:
            self.view.show_message_box("Error", self.model.translate("error_export"), "error")

    def delete_selection(self, index):
        if self.view.show_message_box("Delete Record", self.model.translate("delete_history_confirm"), "question"):
            self.model.delete_history(index)   

    def import_history_from_file(self, filepath):
        success = self.model.import_history(filepath)
        if success:
            self.view.show_message_box("Success", self.model.translate("success_import"), "info")
            return self.model.history # Return the list to the View for refreshing
        else:
            self.view.show_message_box("Error", self.model.translate("error_import"), "error")
            return None

    def change_language(self, new_lang):
        self.model.current_lang = new_lang
        self.refresh_language()

    def refresh_language(self):
        lang = self.model.languages[self.model.current_lang]
        self.view.rebuild_main_frame(lang)
        self.view.menu_bar.rebuild_barmenu(lang)
        self.view.update_daily_goals(self.model.get_progress(), self.model.get_goals(), lang)

    def launch_game(self, game_id, difficulty):
        if self.model.is_active:
            self.view.show_message_box("Warning", self.model.translate("game_in_progress"), "warning")
            return
        lang = self.model.languages[self.model.current_lang]
        self.model.is_active = True
        self.view.prepare_game_layout()
        config = self.model.difficulty_config[difficulty]
        self.model.time_limit = config["time"]
        self.model.start_time = time.time()
        self.current_game = self.view.create_game_board(lang)
        self.root.update_idletasks()
        self.model.notify_game = self.current_game.render
        self.current_game.canvas.update_idletasks()
        self.model.w, self.model.h = self.current_game.canvas.winfo_width(), self.current_game.canvas.winfo_height()
        self.model.w = max(self.model.w, 300)
        self.model.h = max(self.model.h, 200)
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
        self.view.display_game_message(self.model.translate("memorize"), "blue", self.model.w, self.model.h)
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
        if self.model.reaction_state == "ready": 
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
        self.model.configure_typing_text()
        
        if self.model.current_char_index >= len(self.model.target_text):
            self.end_game(self.model.translate("victory_msg"), "blue")

    def check_time(self):
        if not self.model.is_active: 
            return   
        time_left = self.model.get_remaining_time()  
        # Update the HUD timer every 100ms
        self.view.update_hud(self.model.current_score, time_left, self.model.languages[self.model.current_lang])

        if time_left <= 0:
            self.end_game(self.model.translate("time_up"), "red")
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
                        self.end_game(self.model.translate("victory_msg"), "green")
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
        self.view.update_hud(self.model.current_score, remaining, self.model.languages[self.model.current_lang])

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
                    self.end_game(self.model.translate("victory_msg"), "green")
            else:
                # WRONG
                self.handle_score(-2)
                self.view.display_game_message(self.model.translate("wrong"), "red", self.model.w, self.model.h)
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
        username = self.view.create_result_dialog(self.model.translate("game_over"), message, elapsed, score, self.model.languages[self.model.current_lang])
        # 3. Save the record with the username
        self.model.save_record(
            username,
            self.model.current_game, 
            self.model.current_difficulty, 
            elapsed, 
            score
        )
        self.model.add_progress()
        self.view.main_frame.destroy()
        self.current_game = None
        self.refresh_language()
        self.model.current_score = 0
