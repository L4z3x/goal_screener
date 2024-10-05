import sys,ctypes,os,json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QLineEdit, QMessageBox, QHBoxLayout, QListWidget,
    QTextEdit, QScrollArea
)
from PyQt5.QtGui import QPixmap, QColor
from PIL import Image, ImageDraw, ImageFont
import traceback 

class WallpaperApp(QWidget):
    mainQ = {}
    sideQ = {}
    selected_item = ''
    tracked_item = ''
    image_path =''
    ICON_PATH ="./quest_icon.png"
    FONT = "/home/lazex/ttf-comic-mono-git/src/comic-mono-font/ComicMono.ttf"
    def __init__(self):
        super().__init__()
        self.initUI()
        self.retreiveD()
        self.update_quest_list()
        self.selected_quest_index = None

    def initUI(self):
        self.setWindowTitle('Goal_Screener')

        # Main layout (split horizontally into two sections)
        main_layout = QVBoxLayout()

        # Top section layout (split vertically into two)
        top_layout = QHBoxLayout()

        # Left side (Quest list)
        self.quest_list_widget = QListWidget()
        self.quest_list_widget.itemClicked.connect(self.on_quest_clicked)

        # Right side (Description display with text wrapping and scrolling)
        self.description_label = QTextEdit()
        self.description_label.setReadOnly(True)
        self.description_label.setWordWrapMode(True)  # Enable text wrapping

        # Scroll area for description
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.description_label)

        # Add quest list and description to the top layout
        top_layout.addWidget(self.quest_list_widget)
        top_layout.addWidget(scroll_area)

        # Bottom section (inputs and buttons)
        bottom_layout = QVBoxLayout()

        # Set up the image upload area
        self.img_label = QLabel("No image selected")
        self.upload_btn = QPushButton("Upload Image", self)
        self.upload_btn.clicked.connect(self.upload_image)

        # Goal input
        self.goal_input = QLineEdit(self)
        self.goal_input.setPlaceholderText("Enter a Quest")

        # Goal description input
        self.goal_des = QLineEdit(self)
        self.goal_des.setPlaceholderText("Enter a brief description")

        # Add buttons
        self.addTaskMain_btn = QPushButton("Add", self)
        self.addTaskMain_btn.clicked.connect(self.chooseTask)

        #Track button
        if self.tracked_item :
            self.track_label = QLabel(f"Tracking: {self.tracked_item}")
        else:
            self.track_label = QLabel("Tracking: Nothing Right Now")
        self.track_btn = QPushButton("Track")
        self.track_btn.clicked.connect(self.trackTask)

        self.remove_btn = QPushButton("Remove", self)
        self.remove_btn.clicked.connect(self.removeTask)

        # Add widgets to bottom layout
        bottom_layout.addWidget(self.img_label)
        bottom_layout.addWidget(self.track_label)        
        bottom_layout.addWidget(self.upload_btn)
        bottom_layout.addWidget(self.goal_input)
        bottom_layout.addWidget(self.goal_des)
        bottom_layout.addWidget(self.addTaskMain_btn)
        bottom_layout.addWidget(self.track_btn)
        bottom_layout.addWidget(self.remove_btn)

        # Add top and bottom sections to the main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)
        self.image_path = None

    def chooseTask(self):
        # Create a message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Choose Quest Type")
        msg_box.setText("Do you want to add a Main Quest or a Side Quest?")
        
        # Add custom buttons for Main, Side, and Cancel
        main_button = msg_box.addButton("Main Quest", QMessageBox.ActionRole)
        side_button = msg_box.addButton("Side Quest", QMessageBox.ActionRole)
        cancel_button = msg_box.addButton(QMessageBox.Cancel)
        
        # Show the message box and wait for the user's response
        msg_box.exec_()
        
        # Check which button was clicked
        if msg_box.clickedButton() == main_button:
            self.add_task_main()  # Call the method to add a Main Quest
        elif msg_box.clickedButton() == side_button:
            self.add_task_side()  # Call the method to add a Side Quest
        elif msg_box.clickedButton() == cancel_button:
            pass  # Do nothing if "Cancel" is clicked
        
    def trackTask(self):
        if self.selected_item:  # Check if a quest is selected
            self.tracked_item = self.selected_item
            self.track_label.setText(f"Tracking: {self.tracked_item}")  # Update the label with the selected quest
            self.on_submit()
        else:
            QMessageBox.warning(self, "Note", "Please select a quest to track.")

    def removeTask(self):
        item = self.selected_item
        if item in self.mainQ:
            del self.mainQ[item]
        if item in self.sideQ:
            del self.sideQ[item]
        self.update_quest_list()
        self.on_submit()

    def retreiveD(self):
        with open("Quest.json", "r") as file:
            try:
                data = json.load(file)
                self.mainQ = data[0]
                self.sideQ = data[1]
                self.tracked_item = data[2]
                self.image_path = data[3]
                self.img_label.setText(self.image_path)
                pixmap = QPixmap(self.image_path)
                self.img_label.setPixmap(pixmap.scaled(200, 200))
                self.track_label.setText(f"Tracking: {self.tracked_item}")
            except Exception as e:
                print(f'Error:{e}')
            
    def writeD(self):
        with open("./Quest.json", "w") as file:
            data = [self.mainQ, self.sideQ,self.tracked_item,self.image_path]
            json.dump(data, file, indent=4)

    def add_task_main(self):
        quest = self.goal_input.text()
        des = self.goal_des.text()
        if quest and des:
            if quest not in self.mainQ.keys():
                self.mainQ[quest] = des
                self.update_quest_list()
                print(self.mainQ)
            else:
                QMessageBox.warning(self, "Quest existing", "Please enter another Quest.")
            self.on_submit()
            return
        QMessageBox.warning(self, "Input Missing", "Please Complete your Quest.")
        return

    def add_task_side(self):
        quest = self.goal_input.text()
        des = self.goal_des.text()
        if quest and des:
            if quest not in self.sideQ.keys():
                self.sideQ[quest] = des
                self.update_quest_list()
                print(self.sideQ)
            else:
                QMessageBox.warning(self, "Quest existing", "Please enter another Quest.")
            self.on_submit()
            return
        QMessageBox.warning(self, "Input Missing", "Please Complete your Quest.")
        return

    def update_quest_list(self):
        self.quest_list_widget.clear()  
        for quest in self.mainQ.keys():
            self.quest_list_widget.addItem(quest)
        for quest in self.sideQ.keys():
            self.quest_list_widget.addItem(quest)

    def on_quest_clicked(self, item):
        self.selected_item = item.text()
        quest_text = item.text()
        self.selected_quest_index = self.quest_list_widget.row(item)
        self.description_label.setPlainText(
            self.mainQ.get(quest_text, self.sideQ.get(quest_text, "No description available."))
        )
        for i in range(self.quest_list_widget.count()):
            if self.quest_list_widget.item(i) == item:
                self.quest_list_widget.item(i).setBackground(QColor('blue'))
            else:
                self.quest_list_widget.item(i).setBackground(QColor('white'))

    def upload_image(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if self.image_path:
            self.img_label.setText(self.image_path)
            pixmap = QPixmap(self.image_path)
            self.img_label.setPixmap(pixmap.scaled(200, 200))
    
    def generate_image_with_text(self):
        try:
            img = Image.open(self.image_path)
            draw = ImageDraw.Draw(img)
            icon_path = self.ICON_PATH
            font = ImageFont.truetype(self.FONT, 60)  
            font2 = ImageFont.truetype(self.FONT, 35 )  
            font3 = ImageFont.truetype("/home/lazex/ttf-comic-mono-git/src/comic-mono-font/ComicMono-Bold.ttf", 80 )  

            icon = Image.open(icon_path)
            icon_size = 100
            icon = icon.resize((icon_size, icon_size))
            
            def cut_text(quest, des):
                def cut_at_space(text, max_len):
                    if len(text) > max_len:
                        
                        last_space = text.rfind(' ', 0, max_len)
                        if last_space != -1:  
                            return text[:last_space] + "..."
                        else:  
                            return text[:max_len] + "..."
                    return text

                quest = cut_at_space(quest, MAX_STR)
                des = cut_at_space(des, MAX_STR)
                
                return quest, des

            # Image size
            W, H = img.size
            text_gap = 200 

            # quest limit
            QUEST_LIMIT = 5
            MAX_STR = 37
            # Coordinates for main quests (left side)
            y_main = int(W / 7)
            x_main = int(H / 5)  # Align to the left side
            
            # Drawing Quest Title 
            draw.text((x_main + 190, y_main - 210), "MAIN QUESTS", fill="white",font=font3)

            # Coordinates for side quests (right side)
            y_side = y_main
            x_side = W - x_main - 900  
            
            # Drawing Quest Title 
            draw.text((x_side + 190, y_side - 210), "SIDE QUESTS", fill="white",font=font3)

            # Render Main Quests on the left
            for i, quest in enumerate(self.mainQ.keys()):
                if i == QUEST_LIMIT:
                    break  # Limit to 4 main quests
                des = self.mainQ[quest]
                text,text2 = cut_text(quest,des)
                
                
                # Draw rounded rectangle for main quest
                draw.rounded_rectangle(
                    [(x_main  - 20, y_main - 20), (x_main + 900, y_main + 150)],
                    fill=(40, 39, 50), outline="black", width=3, radius=20
                )
                
                # Draw icon
                if quest == self.tracked_item:
                    icon_x = x_main 
                    img.paste(icon, (int(icon_x), int(y_main + 10)), icon) 

                # Draw text
                draw.text((x_main + 120, y_main + 25), text, fill="white", font=font)
                draw.text((x_main + 120, y_main + 95), text2, fill="white", font=font2)
                
                
                # Update vertical position for the next quest
                y_main += text_gap
            
            # Render Side Quests on the right
            for i, quest in enumerate(self.sideQ.keys()):
                if i == QUEST_LIMIT:
                    break  # Limit to 4 side quests
                
                des = self.sideQ[quest]
                text,text2 = cut_text(quest,des)
                text = f"{quest}"
                text2 = f"{des}"
                
                # Draw rounded rectangle for side quest
                draw.rounded_rectangle(
                    [(x_side - 20, y_side - 20), (x_side + 900, y_side + 150)],
                    fill=(40, 39, 50), outline="black", width=3, radius=20
                )
                
                # Draw icon (aligned to the right)
                if quest == self.tracked_item:
                    icon_x = x_side   # Adjust icon position relative to the text
                    img.paste(icon, (int(icon_x), int(y_side + 10)), icon)

                # Draw text (aligned to the right)
                draw.text((x_side + 120, y_side + 25), text, fill="white", font=font)
                draw.text((x_side + 120, y_side+ 95), text2, fill="white", font=font2)
                
                
                
                # Update vertical position for the next quest
                y_side += text_gap
            
            # Save the output image
            output_path = "output_image.png"
            img.save(output_path)
            return output_path
        
        except Exception as e:
            error_trace = traceback.format_exc()
            QMessageBox.critical(self, "Error", f"Failed to generate image: {e} {error_trace}")

    def set_wallpaper_windows(self, image_path):
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            QMessageBox.information(self, "Success", "Wallpaper set successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set wallpaper: {e}")

    def set_wallpaper_linux(self, image_path):
        try:
            os.system(f"gsettings set org.gnome.desktop.background picture-uri /home/lazex/goal_Screener/{image_path}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri-dark /home/lazex/goal_Screener/{image_path}")
            QMessageBox.information(self, "Success", f"Wallpaper set successfully! {image_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set wallpaper: {e}")

    def set_wallpaper(self, image_path):
        if os.name == 'nt':  # Windows
            self.set_wallpaper_windows(image_path)
        else:  # Linux
            self.set_wallpaper_linux(image_path)

    def on_submit(self):
        if not self.image_path:
            QMessageBox.warning(self, "Input Missing", "Please upload an image.")
            return

        if not self.mainQ and not self.sideQ:
            QMessageBox.warning(self, "Input Missing", "Please enter your goals or quests.")
            return
        self.writeD()
        output_image = self.generate_image_with_text()
        if output_image:
            self.set_wallpaper(output_image)


def main():
    app = QApplication(sys.argv)
    window = WallpaperApp()
    window.resize(1000, 800)  # Adjust window size
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()