import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
import io
import os
from urllib.request import urlopen
import webbrowser
import json
import re


class RecipeExplorerApp:  # New creative name for the app
    def __init__(self, root):
        self.root = root
        self.root.title("🍳 გემო - თქვენი კულინარიული ასისტენტი")  # Updated title
        self.root.geometry("1200x800")
        self.root.minsize(900, 700)
        self.root.configure(bg="#FDF7F0")

        # API Configuration
        self.api_key = "4804f0fb593d401a9e91df310b8ab41e"  # Replace with your key
        self.base_url = "https://api.spoonacular.com"
        self.saved_recipes = []  # List to store Spoonacular saved recipes

        # Local Recipes Configuration (User-added recipes)
        self.local_recipes_file = "my_recipes.json"
        self.my_recipes = []
        self.load_my_recipes()

        # Built-in Georgian Recipes Configuration
        self.georgian_db_file = "georgian_recipes_db.json"
        self.built_in_georgian_recipes = []
        self.load_built_in_georgian_recipes()

        # UI Initialization
        self.setup_ui()

        # Load default recipes on startup
        self.load_random_recipes()

    def load_my_recipes(self):
        """Loads locally stored recipes from a JSON file."""
        if os.path.exists(self.local_recipes_file):
            try:
                with open(self.local_recipes_file, 'r', encoding='utf-8') as f:
                    self.my_recipes = json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("შეცდომა",
                                     "მოხდა შეცდომა ლოკალური რეცეპტების ფაილის წაკითხვისას. ფაილი შეიძლება დაზიანებული იყოს.")
                self.my_recipes = []
        else:
            self.my_recipes = []

    def save_my_recipes(self):
        """Saves locally created recipes to a JSON file."""
        try:
            with open(self.local_recipes_file, 'w', encoding='utf-8') as f:
                json.dump(self.my_recipes, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("შეცდომა", f"ვერ მოხერხდა ლოკალური რეცეპტების შენახვა: {e}")

    def load_built_in_georgian_recipes(self):
        """Loads built-in Georgian recipes from a JSON file."""
        if os.path.exists(self.georgian_db_file):
            try:
                with open(self.georgian_db_file, 'r', encoding='utf-8') as f:
                    self.built_in_georgian_recipes = json.load(f)
                    for recipe in self.built_in_georgian_recipes:
                        recipe['is_built_in_georgian'] = True  # Flag to distinguish built-in recipes
            except json.JSONDecodeError:
                messagebox.showerror("შეცდომა",
                                     "მოხდა შეცდომა ჩაშენებული ქართული რეცეპტების ფაილის წაკითხვისას. ფაილი შეიძლება დაზიანებული იყოს.")
                self.built_in_georgian_recipes = []
        else:
            messagebox.showwarning("გაფრთხილება",
                                   f"ჩაშენებული ქართული რეცეპტების ფაილი '{self.georgian_db_file}' ვერ მოიძებნა. ზოგიერთი ფუნქციონალი შეიძლება არ იმუშაოს.")
            self.built_in_georgian_recipes = []

    def setup_ui(self):
        """Sets up the application's user interface."""
        self.main_frame = tk.Frame(self.root, bg="#FDF7F0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header Section
        header_frame = tk.Frame(self.main_frame, bg="#FDF7F0")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            header_frame,
            text="🍳 გემო",  # Updated app name
            font=("Arial", 28, "bold"),
            bg="#FDF7F0",
            fg="#4A4A4A"
        ).pack(side=tk.LEFT, padx=10)

        # Buttons on the right side of the header
        button_frame = tk.Frame(header_frame, bg="#FDF7F0")
        button_frame.pack(side=tk.RIGHT, padx=10)

        ttk.Button(
            button_frame,
            text="შენახული Spoonacular რეცეპტები",
            command=self.show_saved_recipes,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)  # Reduced padx between buttons

        ttk.Button(
            button_frame,
            text="ჩემი რეცეპტები/იდეები",
            command=self.show_my_recipes,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # Search and Filters Section
        controls_frame = tk.Frame(self.main_frame, bg="#FDF7F0", padx=10, pady=10, bd=1, relief="solid",
                                  highlightbackground="#E0E0E0")
        controls_frame.pack(fill=tk.X, pady=10)

        # Search Entry and Button
        search_sub_frame = tk.Frame(controls_frame, bg="#FDF7F0")
        search_sub_frame.pack(fill=tk.X, pady=5)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_sub_frame,
            textvariable=self.search_var,
            width=60,
            font=("Arial", 12),
            style="TEntry"
        )
        search_entry.pack(side=tk.LEFT, padx=5, ipady=4, expand=True, fill=tk.X)

        ttk.Button(
            search_sub_frame,
            text="ძებნა",
            command=self.search_recipes,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_sub_frame,
            text="შემთხვევითი რეცეპტები",
            command=self.load_random_recipes,
            style="TButton"
        ).pack(side=tk.LEFT, padx=5)

        # Filters
        filters_sub_frame = tk.Frame(controls_frame, bg="#FDF7F0")
        filters_sub_frame.pack(fill=tk.X, pady=5)

        # Category Filter
        tk.Label(filters_sub_frame, text="კატეგორია:", font=("Arial", 10), bg="#FDF7F0", fg="#555").pack(side=tk.LEFT,
                                                                                                         padx=5)
        self.category_var = tk.StringVar()
        categories = ["ყველა", "მთავარი კერძი", "საუზმე", "სადილი", "ვეგანური", "დესერტი", "იტალიური", "ქართული",
                      "ამერიკული", "მექსიკური", "ფრანგული"]
        category_menu = ttk.Combobox(filters_sub_frame, textvariable=self.category_var, values=categories,
                                     state="readonly", font=("Arial", 10), width=15)
        category_menu.current(0)
        category_menu.pack(side=tk.LEFT, padx=5)

        # Diet Filter
        tk.Label(filters_sub_frame, text="დიეტა:", font=("Arial", 10), bg="#FDF7F0", fg="#555").pack(side=tk.LEFT,
                                                                                                     padx=15)
        self.diet_var = tk.StringVar()
        diets = ["ყველა", "ვეგანური", "ვეგეტარიანული", "გლუტენის გარეშე", "კეტო", "პალეო", "რძის გარეშე",
                 "თხილის გარეშე"]
        diet_menu = ttk.Combobox(filters_sub_frame, textvariable=self.diet_var, values=diets, state="readonly",
                                 font=("Arial", 10), width=15)
        diet_menu.current(0)
        diet_menu.pack(side=tk.LEFT, padx=5)

        # Max Time Filter
        tk.Label(filters_sub_frame, text="მაქს. დრო (წთ):", font=("Arial", 10), bg="#FDF7F0", fg="#555").pack(
            side=tk.LEFT, padx=15)
        self.time_var = tk.IntVar(value=0)
        ttk.Spinbox(filters_sub_frame, from_=0, to=300, increment=15, textvariable=self.time_var, width=6,
                    font=("Arial", 10)).pack(
            side=tk.LEFT, padx=5)

        # Recipe Display Area
        self.recipes_canvas = tk.Canvas(self.main_frame, bg="#FDF7F0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.recipes_canvas.yview)
        self.recipes_frame = tk.Frame(self.recipes_canvas, bg="#FDF7F0")

        self.recipes_frame.bind(
            "<Configure>",
            lambda e: self.recipes_canvas.configure(
                scrollregion=self.recipes_canvas.bbox("all")
            )
        )

        self.recipes_canvas.create_window((0, 0), window=self.recipes_frame, anchor="nw")
        self.recipes_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.recipes_canvas.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 5))
        self.scrollbar.pack(side="right", fill="y")

        # Configure styles
        self.setup_styles()

        # Bind Enter key to search
        search_entry.bind('<Return>', lambda event: self.search_recipes())

    def setup_styles(self):
        """Configures ttk styles for a more modern look."""
        style = ttk.Style()

        # General Button Style
        style.configure("TButton",
                        font=("Arial", 10),
                        background="#E8E8E8",
                        foreground="#333",
                        padding=6,
                        relief="flat")
        style.map("TButton",
                  background=[("active", "#D0D0D0")],
                  foreground=[("active", "#000")])

        # Accent Button Style (for primary actions)
        style.configure("Accent.TButton",
                        font=("Arial", 10, "bold"),
                        foreground="#fff",
                        background="#FF6F61",
                        padding=6,
                        relief="flat")
        style.map("Accent.TButton",
                  background=[("active", "#E05A4D")])

        # Entry Style
        style.configure("TEntry",
                        fieldbackground="white",
                        foreground="#333",
                        padding=(5, 5))

        # Combobox Style
        style.configure("TCombobox",
                        fieldbackground="white",
                        foreground="#333",
                        padding=(3, 3))
        style.map("TCombobox",
                  fieldbackground=[('readonly', 'white')])

        # Scrollbar Style
        style.configure("Vertical.TScrollbar",
                        background="#E0E0E0",
                        troughcolor="#F0F0F0",
                        bordercolor="#E0E0E0",
                        gripcount=0)
        style.map("Vertical.TScrollbar",
                  background=[("active", "#C0C0C0")])

        # Notebook (Tabs) Style
        style.configure("TNotebook", background="#FDF7F0", borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#E0E0E0",
                        foreground="#555",
                        padding=[10, 5],
                        font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#FF6F61")],
                  foreground=[("selected", "white")])

    def make_api_request(self, endpoint, params=None):
        """Makes an API request to Spoonacular."""
        if params is None:
            params = {}

        params['apiKey'] = self.api_key
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API შეცდომა", f"შეცდომა API მოთხოვნისას: {str(e)}\n"
                                                f"გთხოვთ, შეამოწმოთ თქვენი ინტერნეტ კავშირი ან API გასაღები.")
            return None

    def load_random_recipes(self):
        """Loads a batch of random recipes, mixing Spoonacular and Georgian."""
        params = {
            'number': 9,
            'tags': self.get_selected_filters().get('tags', '')  # Tags filter might not apply well to random
        }

        # Fetch Spoonacular random recipes
        data = self.make_api_request("recipes/random", params)
        spoonacular_recipes = data['recipes'] if data and 'recipes' in data else []

        # Mix with random built-in Georgian recipes
        import random
        num_georgian_to_add = min(3, len(self.built_in_georgian_recipes))  # Add up to 3 Georgian recipes
        random_georgian_recipes = random.sample(self.built_in_georgian_recipes, num_georgian_to_add)

        all_recipes = spoonacular_recipes + random_georgian_recipes
        random.shuffle(all_recipes)  # Shuffle to mix them up

        if all_recipes:
            self.display_recipes(all_recipes)
        else:
            messagebox.showinfo("ინფორმაცია", "ვერ მოხერხდა შემთხვევითი რეცეპტების ჩატვირთვა. სცადეთ მოგვიანებით.")

    def search_recipes(self):
        """Searches for recipes based on user input and filters across all sources."""
        query = self.search_var.get().strip().lower()

        # --- Spoonacular Search ---
        spoonacular_params = {
            'number': 24,
            'instructionsRequired': True,
            'addRecipeInformation': True,
            'fillIngredients': True,
            **self.get_selected_filters()
        }
        if query:
            spoonacular_params['query'] = query

        spoonacular_data = self.make_api_request("recipes/complexSearch", spoonacular_params)
        spoonacular_results = spoonacular_data['results'] if spoonacular_data and 'results' in spoonacular_data else []

        # Fetch full details for Spoonacular results if needed
        if spoonacular_results and not all('extendedIngredients' in r for r in spoonacular_results):
            recipe_ids = [str(recipe['id']) for recipe in spoonacular_results if 'id' in recipe]
            if recipe_ids:
                details_data = self.make_api_request("recipes/informationBulk", {'ids': ','.join(recipe_ids)})
                if details_data:
                    detailed_results_map = {d['id']: d for d in details_data}
                    spoonacular_results = [detailed_results_map[r['id']] for r in spoonacular_results if
                                           r['id'] in detailed_results_map]

        # --- Local (User-added) and Built-in Georgian Recipes Search ---
        all_local_and_georgian_recipes = self.my_recipes + self.built_in_georgian_recipes
        filtered_custom_recipes = []

        for recipe in all_local_and_georgian_recipes:
            match_query = True
            match_category = True
            match_time = True

            # Query matching: check title, ingredients, instructions
            if query:
                recipe_text = f"{recipe.get('title', '')} {recipe.get('ingredients', '')} {recipe.get('instructions', '')}".lower()
                if query not in recipe_text:
                    match_query = False

            # Category matching
            selected_category = self.category_var.get()
            if selected_category != "ყველა":
                recipe_category = recipe.get('category', '').lower()
                mapped_selected_category = self.get_selected_filters().get(
                    'cuisine') or self.get_selected_filters().get('type')

                if mapped_selected_category and mapped_selected_category not in recipe_category:
                    match_category = False
                elif not mapped_selected_category and selected_category.lower() not in recipe_category:
                    match_category = False  # Fallback if map not found, compare directly

            # Max Time matching
            max_time = self.time_var.get()
            if max_time > 0 and recipe.get('time', 0) > max_time:
                match_time = False

            if match_query and match_category and match_time:
                filtered_custom_recipes.append(recipe)

        # --- Combine all results and remove duplicates ---
        all_results = spoonacular_results + filtered_custom_recipes

        unique_results = []
        seen_titles = set()
        for recipe in all_results:
            title = recipe.get('title', 'NO_TITLE_').lower()
            if title not in seen_titles:
                unique_results.append(recipe)
                seen_titles.add(title)

        self.display_recipes(unique_results)

    def get_selected_filters(self):
        """Returns the selected filters as a dictionary for API parameters."""
        filters = {}

        category = self.category_var.get()
        if category != "ყველა":
            category_map = {
                "მთავარი კერძი": "main course",
                "საუზმე": "breakfast",
                "სადილი": "lunch",
                "ვეგანური": "vegan",
                "დესერტი": "dessert",
                "იტალიური": "italian",
                "ქართული": "georgian",
                "ამერიკული": "american",
                "მექსიკური": "mexican",
                "ფრანგული": "french"
            }
            mapped_category = category_map.get(category, category.lower())

            if mapped_category in ["italian", "georgian", "american", "mexican", "french"]:
                filters['cuisine'] = mapped_category
            else:
                filters['type'] = mapped_category

        diet = self.diet_var.get()
        if diet != "ყველა":
            diet_map = {
                "ვეგანური": "vegan",
                "ვეგეტარიანული": "vegetarian",
                "გლუტენის გარეშე": "gluten free",
                "კეტო": "ketogenic",
                "პალეო": "paleo",
                "რძის გარეშე": "dairy free",
                "თხილის გარეშე": "nut free"
            }
            filters['diet'] = diet_map.get(diet, diet.lower())

        max_time = self.time_var.get()
        if max_time > 0:
            filters['maxReadyTime'] = max_time

        return filters

    def display_recipes(self, recipes):
        """Displays recipes in the main GUI area."""
        for widget in self.recipes_frame.winfo_children():
            widget.destroy()

        if not recipes:
            no_results = tk.Label(
                self.recipes_frame,
                text="რეცეპტები არ მოიძებნა. სცადეთ შეცვალოთ ძებნის პარამეტრები.",
                font=("Arial", 16, "italic"),
                bg="#FDF7F0",
                fg="#777"
            )
            no_results.pack(pady=50, padx=20)
            return

        column_count = 3
        for i, recipe in enumerate(recipes):
            # Determine if it's a local/built-in recipe or Spoonacular
            is_custom_source = recipe.get('is_local', False) or recipe.get('is_built_in_georgian', False)
            row = i // column_count
            col = i % column_count
            self.create_recipe_card(recipe, row, col, parent_frame=self.recipes_frame,
                                    is_custom_source=is_custom_source)

        self.root.update_idletasks()
        self.recipes_canvas.config(scrollregion=self.recipes_canvas.bbox("all"))

    def create_recipe_card(self, recipe, row, col, parent_frame, is_custom_source=False):
        """Creates and places a single recipe card in the specified parent frame grid."""
        card = tk.Frame(
            parent_frame,
            bg="white",
            bd=1,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            highlightbackground="#EFEFEF",
            highlightthickness=1,
            cursor="hand2"
        )
        card.grid(row=row, column=col, pady=10, padx=10, sticky="nsew")

        card.bind("<Button-1>", lambda e, r=recipe: self.show_recipe_details(r, is_custom_source=is_custom_source))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, r=recipe: self.show_recipe_details(r, is_custom_source=is_custom_source))

        img_label_frame = tk.Frame(card, bg="white")
        img_label_frame.pack(pady=5)

        photo = None
        image_loaded = False

        # Prioritize local/built-in image path
        image_path = recipe.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((180, 120))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(img_label_frame, image=photo, bg="white")
                img_label.image = photo
                img_label.pack()
                image_loaded = True
            except Exception as e:
                print(f"Error loading local/built-in image {image_path}: {e}")
        elif not is_custom_source and recipe.get('image', ''):  # Handle Spoonacular images
            try:
                response = requests.get(recipe['image'], stream=True)
                response.raise_for_status()
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img.thumbnail((180, 120))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(img_label_frame, image=photo, bg="white")
                img_label.image = photo
                img_label.pack()
                image_loaded = True
            except (requests.exceptions.RequestException, ValueError, IOError, SyntaxError) as e:
                print(f"Error loading Spoonacular image for {recipe.get('title', 'N/A')}: {e}")

        if not image_loaded:  # If image couldn't be loaded
            no_img = Image.new('RGB', (180, 120), color='#F0F0F0')
            try:
                draw = ImageDraw.Draw(no_img)
                try:
                    font = ImageFont.truetype("arial.ttf", 14)
                except IOError:
                    font = ImageFont.load_default()  # Fallback font
                draw.text((30, 50), "სურათი აკლია", fill="#777", font=font)
            except Exception as e:
                print(f"Error drawing placeholder text: {e}")
            photo = ImageTk.PhotoImage(no_img)
            img_label = tk.Label(img_label_frame, image=photo, bg="white")
            img_label.image = photo
            img_label.pack()

        name_label = tk.Label(
            card,
            text=recipe.get('title', 'No Title'),
            font=("Arial", 12, "bold"),
            bg="white",
            anchor="w",
            fg="#333",
            wraplength=200,
            justify=tk.LEFT
        )
        name_label.pack(fill=tk.X, pady=(5, 2))

        meta_frame = tk.Frame(card, bg="white")
        meta_frame.pack(fill=tk.X, pady=2)

        # Time display adapted for local/built-in vs Spoonacular
        time_val = recipe.get('readyInMinutes', recipe.get('time', 'N/A'))
        time_text = f"⏱️ {time_val} წუთი"
        tk.Label(
            meta_frame,
            text=time_text,
            font=("Arial", 9),
            bg="white",
            fg="#555"
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Show likes for Spoonacular, category for custom recipes
        if not is_custom_source:
            likes_text = f"❤️ {recipe.get('aggregateLikes', 0)}"
            tk.Label(
                meta_frame,
                text=likes_text,
                font=("Arial", 9),
                bg="white",
                fg="#555"
            ).pack(side=tk.LEFT)
        else:
            category_text = f"კატეგორია: {recipe.get('category', 'N/A')}"
            tk.Label(
                meta_frame,
                text=category_text,
                font=("Arial", 9),
                bg="white",
                fg="#555"
            ).pack(side=tk.LEFT)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill=tk.X, pady=10)

        if not is_custom_source:  # Save button for Spoonacular
            save_button = ttk.Button(
                btn_frame,
                text="შენახვა",
                command=lambda r=recipe: self.save_recipe(r),
                style="TButton"
            )
            save_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        elif recipe.get('is_local', False):  # Edit/Delete for user-added local recipes ONLY
            ttk.Button(
                btn_frame,
                text="რედაქტირება",
                command=lambda r=recipe: self.edit_my_recipe(r),
                style="TButton"
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
            ttk.Button(
                btn_frame,
                text="წაშლა",
                command=lambda r=recipe: self.delete_my_recipe(r),
                style="TButton"
            ).pack(side=tk.LEFT, expand=True, fill=tk.X)

        if not is_custom_source and recipe.get('sourceUrl'):  # Web link for Spoonacular
            ttk.Button(
                btn_frame,
                text="ვებგვერდი",
                command=lambda url=recipe['sourceUrl']: webbrowser.open(url),
                style="TButton"
            ).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Configure columns of the parent frame
        parent_frame.grid_columnconfigure(col, weight=1)

    def save_recipe(self, recipe):
        """Saves a Spoonacular recipe to the in-memory list."""
        if not any(r.get('id') == recipe.get('id') for r in self.saved_recipes):
            self.saved_recipes.append(recipe)
            messagebox.showinfo("შენახულია", f"რეცეპტი '{recipe.get('title', 'N/A')}' წარმატებით შენახულია!")
        else:
            messagebox.showinfo("ინფორმაცია", "ეს რეცეპტი უკვე შენახულია.")

    def show_saved_recipes(self):
        """Displays the list of saved Spoonacular recipes in a new window."""
        saved_window = tk.Toplevel(self.root)
        saved_window.title("შენახული Spoonacular რეცეპტები")
        saved_window.geometry("800x600")
        saved_window.configure(bg="#FDF7F0")

        tk.Label(saved_window, text="ჩემი შენახული Spoonacular რეცეპტები", font=("Arial", 18, "bold"), bg="#FDF7F0",
                 fg="#4A4A4A").pack(pady=15)

        if not self.saved_recipes:
            tk.Label(saved_window, text="შენახული Spoonacular რეცეპტები არ გაქვთ.", font=("Arial", 14, "italic"),
                     bg="#FDF7F0", fg="#777").pack(pady=50)
            return

        saved_canvas = tk.Canvas(saved_window, bg="#FDF7F0", highlightthickness=0)
        saved_scrollbar = ttk.Scrollbar(saved_window, orient="vertical", command=saved_canvas.yview)
        saved_frame = tk.Frame(saved_canvas, bg="#FDF7F0")

        saved_frame.bind(
            "<Configure>",
            lambda e: saved_canvas.configure(scrollregion=saved_canvas.bbox("all"))
        )

        saved_canvas.create_window((0, 0), window=saved_frame, anchor="nw")
        saved_canvas.configure(yscrollcommand=saved_scrollbar.set)

        saved_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        saved_scrollbar.pack(side="right", fill="y")

        # Display saved Spoonacular recipes in one column list
        for recipe in self.saved_recipes:
            saved_card = tk.Frame(
                saved_frame,
                bg="white",
                bd=1,
                relief=tk.FLAT,
                padx=10,
                pady=10,
                highlightbackground="#EFEFEF",
                highlightthickness=1,
                cursor="hand2"
            )
            saved_card.pack(fill=tk.X, pady=5, padx=10)
            saved_card.bind("<Button-1>", lambda e, r=recipe: self.show_recipe_details(r, is_custom_source=False))

            tk.Label(saved_card, text=recipe.get('title', 'No Title'), font=("Arial", 12, "bold"), bg="white",
                     fg="#333", anchor="w").pack(fill=tk.X)
            tk.Label(saved_card, text=f"მომზადების დრო: {recipe.get('readyInMinutes', 'N/A')} წუთი", font=("Arial", 10),
                     bg="white", fg="#555", anchor="w").pack(fill=tk.X)
            tk.Label(saved_card, text=f"წყარო: Spoonacular", font=("Arial", 9, "italic"), bg="white", fg="#777",
                     anchor="w").pack(fill=tk.X)

    def show_my_recipes(self):
        """Displays the list of locally created recipes in a new window."""
        my_recipes_window = tk.Toplevel(self.root)
        my_recipes_window.title("ჩემი რეცეპტები/იდეები")
        my_recipes_window.geometry("900x700")
        my_recipes_window.configure(bg="#FDF7F0")

        header_frame = tk.Frame(my_recipes_window, bg="#FDF7F0")
        header_frame.pack(fill=tk.X, pady=15)
        tk.Label(header_frame, text="ჩემი შენახული რეცეპტები და იდეები", font=("Arial", 18, "bold"), bg="#FDF7F0",
                 fg="#4A4A4A").pack(side=tk.LEFT, padx=10)

        ttk.Button(
            header_frame,
            text="ახალი რეცეპტის დამატება",
            command=lambda: self.add_edit_recipe_window(),  # No recipe passed for new
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=10)

        self.my_recipes_canvas = tk.Canvas(my_recipes_window, bg="#FDF7F0",
                                           highlightthickness=0)  # Make canvas a class attribute for refresh
        my_recipes_scrollbar = ttk.Scrollbar(my_recipes_window, orient="vertical", command=self.my_recipes_canvas.yview)
        self.my_recipes_frame_container = tk.Frame(self.my_recipes_canvas, bg="#FDF7F0")

        self.my_recipes_frame_container.bind(
            "<Configure>",
            lambda e: self.my_recipes_canvas.configure(scrollregion=self.my_recipes_frame_container.bbox("all"))
        )

        self.my_recipes_canvas.create_window((0, 0), window=self.my_recipes_frame_container, anchor="nw")
        self.my_recipes_canvas.configure(yscrollcommand=my_recipes_scrollbar.set)

        self.my_recipes_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        my_recipes_scrollbar.pack(side="right", fill="y")

        self.display_my_recipes()  # Initial display of local recipes

    def display_my_recipes(self):
        """Helper to display/refresh local recipes in the 'My Recipes' window."""
        # Clear previous recipes in the local frame container
        for widget in self.my_recipes_frame_container.winfo_children():
            widget.destroy()

        if not self.my_recipes:
            tk.Label(self.my_recipes_frame_container, text="ჯერ არ გაქვთ შენახული რეცეპტები.",
                     font=("Arial", 14, "italic"), bg="#FDF7F0", fg="#777").pack(pady=50)
            return

        column_count = 2  # 2 columns for user-added local recipes
        for i, recipe in enumerate(self.my_recipes):
            row = i // column_count
            col = i % column_count
            # Use the unified create_recipe_card function, explicitly marking it as local
            self.create_recipe_card(recipe, row, col, parent_frame=self.my_recipes_frame_container,
                                    is_custom_source=True)

        self.root.update_idletasks()  # Refresh main window
        if hasattr(self, 'my_recipes_canvas') and self.my_recipes_canvas.winfo_exists():  # Check if canvas exists
            self.my_recipes_canvas.config(scrollregion=self.my_recipes_frame_container.bbox("all"))

    def add_edit_recipe_window(self, recipe=None):
        """Opens a window to add a new recipe or edit an existing one."""
        is_editing = recipe is not None
        edit_window = tk.Toplevel(self.root)
        edit_window.title(
            "რეცეპტის დამატება/რედაქტირება" if not is_editing else f"რეცეპტის რედაქტირება: {recipe['title']}")
        edit_window.geometry("600x700")
        edit_window.transient(self.root)  # Make it a child of the main window
        edit_window.grab_set()  # Make it modal

        main_frame = tk.Frame(edit_window, bg="#FDF7F0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="რეცეპტის სათაური:", font=("Arial", 11), bg="#FDF7F0").pack(anchor="w", pady=(5, 0))
        title_entry = ttk.Entry(main_frame, font=("Arial", 11))
        title_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(main_frame, text="კატეგორია (მაგ. ქართული, დესერტი):", font=("Arial", 11), bg="#FDF7F0").pack(
            anchor="w", pady=(5, 0))
        category_entry = ttk.Entry(main_frame, font=("Arial", 11))
        category_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(main_frame, text="მომზადების დრო (წუთები):", font=("Arial", 11), bg="#FDF7F0").pack(anchor="w",
                                                                                                     pady=(5, 0))
        time_entry = ttk.Entry(main_frame, font=("Arial", 11))
        time_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(main_frame, text="ინგრედიენტები (თითო ხაზზე):", font=("Arial", 11), bg="#FDF7F0").pack(anchor="w",
                                                                                                        pady=(5, 0))
        ingredients_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 10), height=8, padx=5,
                                                     pady=5)
        ingredients_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        tk.Label(main_frame, text="მომზადების წესი:", font=("Arial", 11), bg="#FDF7F0").pack(anchor="w", pady=(5, 0))
        instructions_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 10), height=10, padx=5,
                                                      pady=5)
        instructions_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Image Path (Optional for local recipes)
        tk.Label(main_frame, text="სურათის ფაილის გზა (ლოკალური):", font=("Arial", 11), bg="#FDF7F0").pack(anchor="w",
                                                                                                           pady=(5, 0))
        image_path_var = tk.StringVar()
        image_path_entry = ttk.Entry(main_frame, textvariable=image_path_var, font=("Arial", 11))
        image_path_entry.pack(fill=tk.X, pady=(0, 5))

        # Browse button for image path
        browse_button = ttk.Button(main_frame, text="დათვალიერება",
                                   command=lambda: self.browse_image_path(image_path_var))
        browse_button.pack(pady=(0, 10), anchor="w")

        if is_editing:
            title_entry.insert(tk.END, recipe.get('title', ''))
            category_entry.insert(tk.END, recipe.get('category', ''))
            time_entry.insert(tk.END, str(recipe.get('time', '')))
            ingredients_text.insert(tk.END, recipe.get('ingredients', ''))
            instructions_text.insert(tk.END, recipe.get('instructions', ''))
            image_path_var.set(recipe.get('image_path', ''))

        def save_handler():
            new_title = title_entry.get().strip()
            new_category = category_entry.get().strip()
            new_time_str = time_entry.get().strip()
            new_ingredients = ingredients_text.get("1.0", tk.END).strip()
            new_instructions = instructions_text.get("1.0", tk.END).strip()
            new_image_path = image_path_var.get().strip()

            if not new_title or not new_ingredients or not new_instructions:
                messagebox.showerror("შეცდომა",
                                     "გთხოვთ, შეავსოთ ყველა აუცილებელი ველი (სათაური, ინგრედიენტები, მომზადების წესი).")
                return

            try:
                new_time = int(new_time_str) if new_time_str else 0
            except ValueError:
                messagebox.showerror("შეცდომა", "მომზადების დრო უნდა იყოს რიცხვი.")
                return

            if is_editing:
                # Update existing recipe
                recipe['title'] = new_title
                recipe['category'] = new_category
                recipe['time'] = new_time
                recipe['ingredients'] = new_ingredients
                recipe['instructions'] = new_instructions
                recipe['image_path'] = new_image_path
                messagebox.showinfo("შენახულია", f"რეცეპტი '{new_title}' განახლებულია!")
            else:
                # Add new recipe
                # Ensure unique ID, especially when mixing with built-in ones.
                # A simple timestamp or UUID would be better for robust systems.
                all_ids = ([r.get('id', 0) for r in self.my_recipes] +
                           [r.get('id', 0) for r in self.built_in_georgian_recipes])
                new_id = max(all_ids) + 1 if all_ids else 1

                new_recipe = {
                    'id': new_id,
                    'title': new_title,
                    'category': new_category,
                    'time': new_time,
                    'ingredients': new_ingredients,
                    'instructions': new_instructions,
                    'image_path': new_image_path,
                    'is_local': True  # Mark as user-added local recipe
                }
                self.my_recipes.append(new_recipe)
                messagebox.showinfo("შენახულია", f"რეცეპტი '{new_title}' დამატებულია!")

            self.save_my_recipes()
            self.display_my_recipes()  # Refresh the list in the 'My Recipes' window
            edit_window.destroy()

        save_button = ttk.Button(main_frame, text="შენახვა", command=save_handler, style="Accent.TButton")
        save_button.pack(pady=10)

    def browse_image_path(self, image_path_var):
        """Allows user to browse for an image file."""
        file_path = filedialog.askopenfilename(
            title="აირჩიეთ სურათის ფაილი",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            image_path_var.set(file_path)

    def edit_my_recipe(self, recipe):
        """Calls the add/edit window with the existing recipe data."""
        self.add_edit_recipe_window(recipe)

    def delete_my_recipe(self, recipe):
        """Deletes a local recipe."""
        if messagebox.askyesno("წაშლა", f"ნამდვილად გსურთ რეცეპტის '{recipe.get('title', 'N/A')}' წაშლა?"):
            self.my_recipes.remove(recipe)
            self.save_my_recipes()
            self.display_my_recipes()  # Refresh the list
            messagebox.showinfo("წაშლილია", f"რეცეპტი '{recipe.get('title', 'N/A')}' წაშლილია.")

    def show_recipe_details(self, recipe, is_custom_source=False):
        """Displays comprehensive details of a selected recipe."""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"რეცეპტი: {recipe.get('title', 'N/A')}")
        details_window.geometry("950x850")
        details_window.minsize(800, 700)
        details_window.configure(bg="#FDF7F0")

        details_canvas = tk.Canvas(details_window, bg="#FDF7F0", highlightthickness=0)
        details_scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=details_canvas.yview)
        details_content_frame = tk.Frame(details_canvas, bg="#FDF7F0")

        details_content_frame.bind(
            "<Configure>",
            lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all"))
        )
        details_canvas.create_window((0, 0), window=details_content_frame, anchor="nw")
        details_canvas.configure(yscrollcommand=details_scrollbar.set)

        details_canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        details_scrollbar.pack(side="right", fill="y")

        # Recipe Image
        img_frame = tk.Frame(details_content_frame, bg="#FDF7F0")
        img_frame.pack(fill=tk.X, pady=10)

        photo = None
        image_loaded = False

        image_path = recipe.get('image_path', '')
        if image_path and os.path.exists(image_path):  # Local/Built-in image
            try:
                img = Image.open(image_path)
                img.thumbnail((700, 400))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(img_frame, image=photo, bg="#FDF7F0")
                img_label.image = photo
                img_label.pack()
                image_loaded = True
            except Exception as e:
                print(f"Error loading local image for details: {e}")
        elif not is_custom_source and recipe.get('image', ''):  # Spoonacular image
            try:
                response = requests.get(recipe['image'], stream=True)
                response.raise_for_status()
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img.thumbnail((700, 400))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(img_frame, image=photo, bg="#FDF7F0")
                img_label.image = photo
                img_label.pack()
                image_loaded = True
            except (requests.exceptions.RequestException, ValueError, IOError, SyntaxError) as e:
                print(f"Error loading Spoonacular image for details: {e}")

        if not image_loaded:
            no_img = Image.new('RGB', (700, 400), color='#F0F0F0')
            try:
                draw = ImageDraw.Draw(no_img)
                font = ImageFont.truetype("arial.ttf", 20)
                draw.text((250, 190), "სურათი აკლია", fill="#777", font=font)
            except Exception as e:
                print(f"Error drawing placeholder for details: {e}")
            photo = ImageTk.PhotoImage(no_img)
            img_label = tk.Label(img_frame, image=photo, bg="#FDF7F0")
            img_label.image = photo
            img_label.pack()

        # Main Info
        info_frame = tk.Frame(details_content_frame, bg="#FDF7F0")
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            info_frame,
            text=recipe.get('title', 'No Title'),
            font=("Arial", 24, "bold"),
            bg="#FDF7F0",
            fg="#333",
            wraplength=800,
            justify=tk.CENTER
        ).pack(pady=(0, 10))

        meta_frame = tk.Frame(info_frame, bg="#FDF7F0")
        meta_frame.pack(pady=5)

        time_val = recipe.get('readyInMinutes', recipe.get('time', 'N/A'))
        tk.Label(
            meta_frame,
            text=f"⏱️ მომზადების დრო: {time_val} წუთი",
            font=("Arial", 12),
            bg="#FDF7F0"
        ).pack(side=tk.LEFT, padx=10)

        if not is_custom_source:  # Spoonacular specific meta info
            tk.Label(
                meta_frame,
                text=f"👥 პორციები: {recipe.get('servings', 'N/A')}",
                font=("Arial", 12),
                bg="#FDF7F0"
            ).pack(side=tk.LEFT, padx=10)

            tk.Label(
                meta_frame,
                text=f"❤️ მოწონება: {recipe.get('aggregateLikes', 0)}",
                font=("Arial", 12),
                bg="#FDF7F0"
            ).pack(side=tk.LEFT, padx=10)
        else:  # Local/Built-in recipe meta info
            tk.Label(
                meta_frame,
                text=f"კატეგორია: {recipe.get('category', 'N/A')}",
                font=("Arial", 12),
                bg="#FDF7F0"
            ).pack(side=tk.LEFT, padx=10)

        # Tabs for Ingredients and Instructions
        notebook = ttk.Notebook(details_content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Ingredients Tab
        ingredients_tab = ttk.Frame(notebook)
        notebook.add(ingredients_tab, text="ინგრედიენტები")

        ingredients_text_area = scrolledtext.ScrolledText(
            ingredients_tab,
            wrap=tk.WORD,
            font=("Arial", 12),
            width=80,
            height=15,
            bg="white",
            fg="#333",
            padx=10,
            pady=10
        )
        ingredients_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ingredients_content = ""
        if not is_custom_source:  # Spoonacular ingredients
            try:
                recipe_id = recipe.get('id')
                if recipe_id:  # Ensure ID exists before making API call
                    ingredients_data = self.make_api_request(f"recipes/{recipe_id}/ingredientWidget.json")
                    if ingredients_data and 'ingredients' in ingredients_data:
                        for ing in ingredients_data['ingredients']:
                            name = ing['name'].capitalize()
                            amount = ing['amount'].get('metric', {}).get('value', 'N/A')
                            unit = ing['amount'].get('metric', {}).get('unit', '')
                            ingredients_content += f"• {name}: {amount} {unit}\n"
                    elif recipe.get('extendedIngredients'):  # Fallback to extendedIngredients from complexSearch
                        for ing in recipe['extendedIngredients']:
                            name = ing.get('name', '').capitalize()
                            amount = ing.get('amount', 'N/A')
                            unit = ing.get('unit', '')
                            ingredients_content += f"• {name}: {amount} {unit}\n"
                    else:
                        ingredients_content = "ინგრედიენტები არ არის ხელმისაწვდომი."
                else:
                    ingredients_content = "რეცეპტის ID არ არის ხელმისაწვდომი ინგრედიენტების მოსაძებნად."
            except Exception as e:
                print(f"Error loading Spoonacular ingredients: {e}")
                ingredients_content = "ინგრედიენტების ჩატვირთვისას მოხდა შეცდომა."
        else:  # Local/Built-in recipe ingredients
            ingredients_content = recipe.get('ingredients', 'ინგრედიენტები არ არის ხელმისაწვდომი.')

        ingredients_text_area.insert(tk.END, ingredients_content)
        ingredients_text_area.config(state=tk.DISABLED)

        # Instructions Tab
        instructions_tab = ttk.Frame(notebook)
        notebook.add(instructions_tab, text="მომზადების წესი")

        instructions_text_area = scrolledtext.ScrolledText(
            instructions_tab,
            wrap=tk.WORD,
            font=("Arial", 12),
            width=80,
            height=15,
            bg="white",
            fg="#333",
            padx=10,
            pady=10
        )
        instructions_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        instructions_content = ""
        if not is_custom_source:  # Spoonacular instructions
            try:
                recipe_id = recipe.get('id')
                if recipe_id:  # Ensure ID exists
                    instructions_data = self.make_api_request(f"recipes/{recipe_id}/analyzedInstructions")
                    if instructions_data and len(instructions_data) > 0 and 'steps' in instructions_data[0]:
                        for step in instructions_data[0]['steps']:
                            instructions_content += f"{step['number']}. {step['step']}\n\n"
                    elif recipe.get('instructions'):  # Fallback if analyzedInstructions not available directly
                        clean_instructions = re.sub(r'<.*?>', '', recipe['instructions'])  # Remove HTML tags
                        instructions_content = clean_instructions
                    else:
                        instructions_content = "მომზადების ინსტრუქციები არ არის ხელმისაწვდომი."
                else:
                    instructions_content = "რეცეპტის ID არ არის ხელმისაწვდომი ინსტრუქციების მოსაძებნად."
            except Exception as e:
                print(f"Error loading Spoonacular instructions: {e}")
                instructions_content = "ინსტრუქციების ჩატვირთვისას მოხდა შეცდომა."
        else:  # Local/Built-in recipe instructions
            instructions_content = recipe.get('instructions', 'მომზადების ინსტრუქციები არ არის ხელმისაწვდომი.')

        instructions_text_area.insert(tk.END, instructions_content)
        instructions_text_area.config(state=tk.DISABLED)

        # Action Buttons
        btn_frame = tk.Frame(details_content_frame, bg="#FDF7F0")
        btn_frame.pack(pady=15)

        ttk.Button(
            btn_frame,
            text="დახურვა",
            command=details_window.destroy,
            style="TButton"
        ).pack(side=tk.LEFT, padx=10)

        if not is_custom_source and recipe.get('sourceUrl', ''):  # Only show source URL for Spoonacular
            ttk.Button(
                btn_frame,
                text="ვებგვერდის ნახვა",
                command=lambda: webbrowser.open(recipe['sourceUrl']),
                style="Accent.TButton"
            ).pack(side=tk.LEFT, padx=10)


# Main execution block
if __name__ == "__main__":
    try:
        # Test if arial.ttf is available, otherwise PIL will fallback or raise an error
        _ = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        print(
            "Warning: arial.ttf not found. Text on placeholder images might not render correctly. Install a suitable font or ensure it's in your system's font paths.")


        # Minimal fallback: If the font is not found, we ensure that ImageFont.truetype doesn't crash the app
        class ImageFont:
            @staticmethod
            def truetype(font, size):
                return ImageFont.load_default()  # Use default if specific font not found

            @staticmethod
            def load_default():
                return None  # Return None if even default cannot be loaded (unlikely)

    root = tk.Tk()
    app = RecipeExplorerApp(root)  # Using the new app name
    root.mainloop()