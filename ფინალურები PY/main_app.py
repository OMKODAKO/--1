import sys
import os
import sqlite3
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit,
    QLabel, QTextEdit, QFileDialog, QScrollArea, QListWidget, QListWidgetItem,
    QMessageBox, QHBoxLayout, QFormLayout, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt

API_KEY = "4804f0fb593d401a9e91df310b8ab41e"


class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("გემო👨‍🍳")
        self.setGeometry(100, 100, 900, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("მოძებნე რეცეპტები (მაგ: Chicken Pasta)...")
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setFixedHeight(40)

        self.search_btn = QPushButton("ძებნა 🔎")
        self.search_btn.clicked.connect(self.search_recipes)
        self.search_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.search_btn.setFixedSize(120, 40)
        self.search_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 8px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )

        self.local_btn = QPushButton("ჩემი რეცეპტები 📚")
        self.local_btn.clicked.connect(self.open_local_recipes)
        self.local_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.local_btn.setFixedSize(180, 40)
        self.local_btn.setStyleSheet(
            "QPushButton { background-color: #008CBA; color: white; border-radius: 8px; }"
            "QPushButton:hover { background-color: #007B9E; }"
        )

        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.search_btn)
        header_layout.addWidget(self.local_btn)
        main_layout.addLayout(header_layout)

        self.result_area = QScrollArea()
        self.result_area.setWidgetResizable(True)
        self.result_area.setStyleSheet("""
            QScrollArea { 
                border: 1px solid #ddd; 
                border-radius: 8px;
                background-color: white;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f1f1f1;
            }
            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
            }
        """)

        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setAlignment(Qt.AlignTop)
        self.result_layout.setSpacing(20)

        self.result_area.setWidget(self.result_container)
        main_layout.addWidget(self.result_area)

        self.setLayout(main_layout)

    def search_recipes(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.information(self, "გაფრთხილება", "გთხოვთ შეიყვანოთ საძიებო სიტყვა.")
            return

        for i in reversed(range(self.result_layout.count())):
            widget = self.result_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        self.search_btn.setEnabled(False)
        self.search_btn.setText("იტვირთება...")
        QApplication.processEvents()

        try:
            url = (
                f"https://api.spoonacular.com/recipes/complexSearch"
                f"?query={keyword}&number=15&addRecipeInformation=true&apiKey={API_KEY}"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if not results:
                no_results_label = QLabel("ვერ მოიძებნა რეცეპტები თქვენი მოთხოვნით. სცადეთ სხვა სიტყვა. 😔")
                no_results_label.setFont(QFont("Arial", 14, QFont.StyleItalic))
                no_results_label.setAlignment(Qt.AlignCenter)
                no_results_label.setStyleSheet("color: #555;")
                self.result_layout.addWidget(no_results_label)
                return

            for recipe in results:
                self.add_recipe_card(recipe)

        except requests.exceptions.Timeout:
            QMessageBox.warning(self, "შეცდომა", "მოთხოვნის ვადა ამოიწურა. გთხოვთ, სცადოთ მოგვიანებით.")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "შეცდომა", f"რეცეპტების წამოღება ვერ მოხერხდა: {e}")
        finally:
            self.search_btn.setEnabled(True)
            self.search_btn.setText("ძებნა 🔎")

    def add_recipe_card(self, recipe):
        name = recipe.get("title", "დასახელება უცნობია")
        image_url = recipe.get("image")
        summary_html = recipe.get("summary", "ინფორმაცია მიუწვდომელია.")
        source_url = recipe.get("sourceUrl", "#")

        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.StyledPanel)
        card_frame.setFrameShadow(QFrame.Raised)
        card_frame.setContentsMargins(15, 15, 15, 15)
        card_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            QFrame:hover {
                background-color: #f0f0f0;
            }
        """)
        card_layout = QHBoxLayout(card_frame)
        card_layout.setSpacing(15)

        image_label = QLabel()
        image_label.setFixedSize(200, 150)
        image_label.setAlignment(Qt.AlignCenter)
        if image_url:
            try:
                image_data = requests.get(image_url, timeout=5).content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                image_label.setPixmap(pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                print(f"Error loading image {image_url}: {e}")
                image_label.setText("სურათი მიუწვდომელია")
                image_label.setFont(QFont("Arial", 10, QFont.StyleItalic))
                image_label.setStyleSheet("color: #777;")
        else:
            image_label.setText("სურათი მიუწვდომელია")
            image_label.setFont(QFont("Arial", 10, QFont.StyleItalic))
            image_label.setStyleSheet("color: #777;")

        text_content_layout = QVBoxLayout()

        name_label = QLabel(f"<b>{name}</b>")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setWordWrap(True)
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        display_summary = summary_html
        if len(display_summary) > 300:
            display_summary = display_summary[:300] + "..."

        summary_label = QLabel()
        summary_label.setTextFormat(Qt.RichText)
        summary_label.setText(display_summary)
        summary_label.setFont(QFont("Arial", 10))
        summary_label.setWordWrap(True)
        summary_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        summary_label.setStyleSheet("color: #444;")

        link_btn = QPushButton("ვრცლად Spoonacular-ზე 🔗")
        link_btn.clicked.connect(lambda _, url=source_url: self.open_url(url))
        link_btn.setFont(QFont("Arial", 10, QFont.Bold))
        link_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; border-radius: 5px; padding: 8px; }"
            "QPushButton:hover { background-color: #0b7dda; }"
        )
        link_btn.setFixedWidth(200)

        text_content_layout.addWidget(name_label)
        text_content_layout.addWidget(summary_label)
        text_content_layout.addStretch(1)
        text_content_layout.addWidget(link_btn, alignment=Qt.AlignRight)

        card_layout.addWidget(image_label)
        card_layout.addLayout(text_content_layout)

        self.result_layout.addWidget(card_frame)

    def open_url(self, url):
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.warning(self, "შეცდომა", f"ბმულის გახსნა ვერ მოხერხდა: {e}")

    def open_local_recipes(self):
        self.hide()
        self.local_window = MyRecipesWindow(self)
        self.local_window.show()


class MyRecipesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_screen = parent
        self.setWindowTitle("ჩემი რეცეპტები 📚")
        self.setGeometry(150, 150, 800, 600)

        # Initialize database
        self.db_path = "recipes.db"
        self.conn = None
        self.cursor = None
        self.connect_db()

        self.setup_ui()
        self.load_recipes()

    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.setup_db()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "შეცდომა", f"მონაცემთა ბაზასთან დაკავშირება ვერ მოხერხდა: {e}")

    def setup_db(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ingredients TEXT,
                    instructions TEXT,
                    image_path TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "შეცდომა", f"მონაცემთა ბაზის ინიციალიზაცია ვერ მოხერხდა: {e}")

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Dark theme for message boxes
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        QApplication.setPalette(palette)

        back_btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("უკან მთავარ მენიუში 🏠")
        self.back_btn.clicked.connect(self.go_back_to_main)
        self.back_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.back_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; border-radius: 8px; padding: 10px; }"
            "QPushButton:hover { background-color: #da190b; }"
        )
        back_btn_layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        back_btn_layout.addStretch(1)
        main_layout.addLayout(back_btn_layout)

        form_group_box = QFrame()
        form_group_box.setFrameShape(QFrame.StyledPanel)
        form_group_box.setFrameShadow(QFrame.Raised)
        form_group_box.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #f0f8ff;
            }
        """)
        form_layout = QFormLayout(form_group_box)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(10)

        input_field_style = """
            QLineEdit, QTextEdit { 
                padding: 8px; 
                border: 1px solid #ddd; 
                border-radius: 5px;
                background-color: white;
            }
        """
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("რეცეპტის დასახელება")
        self.name_input.setStyleSheet(input_field_style)
        self.name_input.setFont(QFont("Arial", 10))

        self.ingredients_input = QTextEdit()
        self.ingredients_input.setPlaceholderText("ინგრედიენტები (თითო ხაზზე)")
        self.ingredients_input.setStyleSheet(input_field_style)
        self.ingredients_input.setFont(QFont("Arial", 10))
        self.ingredients_input.setFixedHeight(80)

        self.instructions_input = QTextEdit()
        self.instructions_input.setPlaceholderText("ინსტრუქცია")
        self.instructions_input.setStyleSheet(input_field_style)
        self.instructions_input.setFont(QFont("Arial", 10))
        self.instructions_input.setFixedHeight(120)

        self.image_input_btn = QPushButton("აირჩიე სურათი 🖼️")
        self.image_input_btn.clicked.connect(self.choose_image)
        self.image_input_btn.setStyleSheet(
            "QPushButton { background-color: #5cb85c; color: white; border-radius: 5px; padding: 8px; }"
            "QPushButton:hover { background-color: #4cae4c; }"
        )
        self.image_input_btn.setFont(QFont("Arial", 10, QFont.Bold))

        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(100, 100)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 1px dashed #aaa;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)

        self.selected_image_path = ""

        image_selection_layout = QHBoxLayout()
        image_selection_layout.addWidget(self.image_input_btn)
        image_selection_layout.addWidget(self.image_preview)
        image_selection_layout.addStretch(1)

        form_layout.addRow(QLabel("დასახელება:"), self.name_input)
        form_layout.addRow(QLabel("ინგრედიენტები:"), self.ingredients_input)
        form_layout.addRow(QLabel("ინსტრუქცია:"), self.instructions_input)
        form_layout.addRow(QLabel("სურათი:"), image_selection_layout)

        main_layout.addWidget(form_group_box)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.add_btn = QPushButton("დამატება ✨")
        self.add_btn.clicked.connect(self.add_recipe)
        self.add_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.add_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )

        self.clear_btn = QPushButton("გასუფთავება 🧹")
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.clear_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.clear_btn.setStyleSheet(
            "QPushButton { background-color: #f0ad4e; color: white; border-radius: 8px; padding: 10px; }"
            "QPushButton:hover { background-color: #ec971f; }"
        )

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.clear_btn)
        main_layout.addLayout(btn_layout)

        self.recipe_list_label = QLabel("ჩემი რეცეპტების სია (ორჯერ დააჭირეთ წასაშლელად):")
        self.recipe_list_label.setFont(QFont("Arial", 11, QFont.Bold))
        main_layout.addWidget(self.recipe_list_label)

        self.recipe_list = QListWidget()
        self.recipe_list.itemDoubleClicked.connect(self.delete_recipe_confirm)
        self.recipe_list.itemClicked.connect(self.display_recipe_details)
        self.recipe_list.setFont(QFont("Arial", 10))
        self.recipe_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #e6f7ff;
            }
            QListWidget::item:selected {
                background-color: #cceeff;
                color: black;
            }
        """)
        main_layout.addWidget(self.recipe_list)

        self.setLayout(main_layout)

    def go_back_to_main(self):
        self.hide()
        if self.parent_screen:
            self.parent_screen.show()

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "აირჩიე სურათი",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            self.selected_image_path = path
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.image_preview.setPixmap(
                    pixmap.scaled(
                        self.image_preview.width(),
                        self.image_preview.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            else:
                self.image_preview.setText("არასწორი ფორმატი")
                self.image_preview.setStyleSheet("color: red;")

    def add_recipe(self):
        name = self.name_input.text().strip()
        ingredients = self.ingredients_input.toPlainText().strip()
        instructions = self.instructions_input.toPlainText().strip()
        image = self.selected_image_path

        if not name:
            QMessageBox.warning(self, "შეცდომა", "რეცეპტის დასახელება სავალდებულოა!")
            return

        try:
            self.cursor.execute(
                "INSERT INTO recipes (name, ingredients, instructions, image_path) VALUES (?, ?, ?, ?)",
                (name, ingredients, instructions, image)
            )
            self.conn.commit()
            QMessageBox.information(self, "წარმატება", "რეცეპტი წარმატებით დაემატა!")
            self.load_recipes()
            self.clear_inputs()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "შეცდომა", f"რეცეპტის დამატება ვერ მოხერხდა: {e}")

    def load_recipes(self):
        try:
            self.recipe_list.clear()
            self.cursor.execute("SELECT id, name, ingredients, instructions, image_path FROM recipes ORDER BY name ASC")
            for row in self.cursor.fetchall():
                item_text = f"{row[1]}"  # Show only name
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, {
                    "id": row[0],
                    "name": row[1],
                    "ingredients": row[2],
                    "instructions": row[3],
                    "image_path": row[4]
                })
                self.recipe_list.addItem(list_item)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "შეცდომა", f"რეცეპტების ჩატვირთვა ვერ მოხერხდა: {e}")

    def delete_recipe_confirm(self, item):
        recipe_data = item.data(Qt.UserRole)
        recipe_id = recipe_data["id"]
        recipe_name = recipe_data["name"]

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("რეცეპტის წაშლა")
        msg.setText(f"ნამდვილად გსურთ რეცეპტის '{recipe_name}' წაშლა?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        # Set dark text for message box
        msg.setStyleSheet("QLabel{ color: black; }")

        confirm = msg.exec_()

        if confirm == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
                self.conn.commit()
                QMessageBox.information(self, "წარმატება", f"რეცეპტი '{recipe_name}' წარმატებით წაიშალა!")
                self.load_recipes()
                self.clear_inputs()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "შეცდომა", f"რეცეპტის წაშლა ვერ მოხერხდა: {e}")

    def display_recipe_details(self, item):
        recipe_data = item.data(Qt.UserRole)
        self.name_input.setText(recipe_data["name"])
        self.ingredients_input.setPlainText(recipe_data["ingredients"])
        self.instructions_input.setPlainText(recipe_data["instructions"])
        self.selected_image_path = recipe_data["image_path"]

        if self.selected_image_path and os.path.exists(self.selected_image_path):
            pixmap = QPixmap(self.selected_image_path)
            if not pixmap.isNull():
                self.image_preview.setPixmap(
                    pixmap.scaled(
                        self.image_preview.width(),
                        self.image_preview.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            else:
                self.image_preview.setText("სურათი დაზიანებულია")
                self.image_preview.setStyleSheet("color: red;")
        else:
            self.image_preview.clear()
            self.image_preview.setText("სურათი არ არის არჩეული")
            self.image_preview.setStyleSheet("color: #777;")

    def clear_inputs(self):
        self.name_input.clear()
        self.ingredients_input.clear()
        self.instructions_input.clear()
        self.image_preview.clear()
        self.image_preview.setText("სურათი არ არის არჩეული")
        self.image_preview.setStyleSheet("color: #777;")
        self.selected_image_path = ""
        self.recipe_list.clearSelection()

    def closeEvent(self, event):
        """Close database connection when window closes"""
        if self.conn:
            self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set style to ensure dark text in message boxes
    app.setStyle("Fusion")

    win = MainScreen()
    win.show()
    sys.exit(app.exec_())