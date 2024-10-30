import ctypes.wintypes
import sys,ctypes,os,json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QLineEdit, QMessageBox, QHBoxLayout, QListWidget,
    QTextEdit, QScrollArea
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5 import QtGui
from PIL import Image, ImageDraw, ImageFont
import traceback 
import yaml
from datetime import datetime

if getattr(sys, 'frozen', False):  # If the app is frozen (compiled with PyInstaller)
    basedir = sys._MEIPASS  # Use the temp folder where PyInstaller unpacks the app
else:
    basedir = os.path.dirname(__file__)  # For development purposes

OUTPUT_IMG_PATH = os.path.join(basedir, "assets", "output_image.png")
ICON_PATH = os.path.join(basedir, "assets", "quest_icon.png")
class WallpaperApp(QWidget):
    mainQ = {}
    sideQ = {}
    QUEST_LIMIT = 5
    MAX_STR = 32
    TRACKING_COLOR=(72, 149, 147)
    TRACKING_COLOR_INT= 7262512 #4740483
    selected_item = ''
    tracked_item = ''
    image_path =''
    FONT =os.path.join(basedir,"./assets/ComicMono.ttf")
    FONT_B = os.path.join(basedir,"./assets/ComicMono-Bold.ttf")
    JSON_PATH = os.path.join(basedir,"./assets/Quest.json")
    YAML_PATH = os.path.join(basedir,"./assets/history.yaml")

    def addHistory(self):
        if not self.selected_item:
            QMessageBox.warning(self,"ERROR",f"no Quest was selected")
            return
        with open(self.YAML_PATH,'r') as f:
           data = yaml.safe_load(f) or {} 
        item = ''
        if self.selected_item in self.mainQ:
            item = self.mainQ[self.selected_item]
        if self.selected_item in self.sideQ:
            item =  self.sideQ[self.selected_item]
        quest = {'desription':f'{item}',
                    'time':f'{datetime.now().strftime("%y-%m-%d %H:%M")}',  
                }
                  
        data[f'{self.selected_item}'] = quest
        # print(data)
        with open(self.YAML_PATH,'w') as f:
            yaml.dump(data,f,default_flow_style=False)

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
        
        #achieved button
        self.achieve_btn = QPushButton("Achieved",self)
        self.achieve_btn.clicked.connect(self.addHistory)
        # remove button
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
        bottom_layout.addWidget(self.achieve_btn)
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
        if self.mainQ or self.sideQ:
            self.on_submit()

    def retreiveD(self):
        with open(self.JSON_PATH, "r") as file:
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
                # print(f'Error:{e}')
            
    def writeD(self):
        with open(self.JSON_PATH, "w") as file:
            try:
                data = [self.mainQ, self.sideQ,self.tracked_item,self.image_path]
                json.dump(data, file, indent=4)
            except Exception as e:
                QMessageBox.warning(self,"ERROR",f"Failed to write : {e}")
    def add_task_main(self):
        quest = self.goal_input.text()
        des = self.goal_des.text()
        if quest and des:
            if quest not in self.mainQ.keys():
                self.mainQ[quest] = des
                self.update_quest_list()
                # print(self.mainQ)
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
                # print(self.sideQ)
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
        if self.quest_list_widget.item(0):
            # print(self.quest_list_widget.item(0).text())
        for i in range(self.quest_list_widget.count()):
            if self.quest_list_widget.item(i).text() == self.tracked_item:
                self.quest_list_widget.item(i).setBackground(QColor(self.TRACKING_COLOR_INT))

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
            elif self.quest_list_widget.item(i).text() == self.tracked_item:
                self.quest_list_widget.item(i).setBackground(QColor(self.TRACKING_COLOR_INT))
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
            W, H = img.size
            ICON_SIZE = int (W / 38.4)
            QUEST_BOX_LENGTH = int(W / 4.26)
            QUEST_BOX_HEIGHT = int (H /14.4)
            QUEST_TITLE_X_POSITION = int (W / 20.211)
            QUEST_TITLE_Y_POSITION = int (H / 9.2857)
            QUEST_TXT_X_POSITION = int (QUEST_BOX_LENGTH/7.5)
            QUEST_TXT_Y_POSITION_M = int ( QUEST_BOX_HEIGHT/6)
            QUEST_TXT_Y_POSITION = int ( QUEST_BOX_HEIGHT/1.568)
            FONT_TITLE = int(H/27)
            FONT_QUEST = int(H/36)
            FONT_DES = int (H/61.714)
            text_gap = int (H/10.8)


            icon = Image.open(ICON_PATH)
            icon = icon.resize((ICON_SIZE, ICON_SIZE))

            font = ImageFont.truetype(self.FONT_B, FONT_QUEST) # 60  
            font2 = ImageFont.truetype(self.FONT, FONT_DES ) # 35 
            font3 = ImageFont.truetype(self.FONT_B, FONT_TITLE ) # 80 

            def cut_text(quest, des):
                def cut_at_space(text, max_len):
                    if len(text) > max_len:
                        
                        last_space = text.rfind(' ', 0, max_len)
                        if last_space != -1:  
                            return text[:last_space] + "..."
                        else:  
                            return text[:max_len] + "..."
                    return text

                quest = cut_at_space(quest, self.MAX_STR)
                des = cut_at_space(des, self.MAX_STR)
                
                return quest, des

            # Image size
            
           
            # print(W,H)
            # quest limit
            
            # Coordinates for main quests (left side)
            y_main = int(W / 7)
            x_main = int(H / 5)  # Align to the left side
            
            # Drawing Quest Title 
            draw.text((x_main + QUEST_TITLE_X_POSITION , y_main - QUEST_TITLE_Y_POSITION), "MAIN QUESTS", fill="white",font=font3)

            # Coordinates for side quests (right side)
            y_side = y_main
            x_side = W - x_main - QUEST_BOX_LENGTH  
            
            # Drawing Quest Title 
            draw.text((x_side + QUEST_TITLE_X_POSITION , y_side - QUEST_TITLE_Y_POSITION), "SIDE QUESTS", fill="white",font=font3)

            # Render Main Quests on the left
            for i, quest in enumerate(self.mainQ.keys()):
                if i == self.QUEST_LIMIT:
                    break  # Limit to 4 main quests
                des = self.mainQ[quest]
                text,text2 = cut_text(quest,des)                
        
                # Draw icon
                if quest == self.tracked_item:
                    draw.rounded_rectangle(
                    [(x_main  - 20, y_main - 20), (x_main + QUEST_BOX_LENGTH, y_main + QUEST_BOX_HEIGHT)],
                    fill=(40, 39, 50), outline=self.TRACKING_COLOR, width=3, radius=20
                    )
                    icon_x = x_main 
                    img.paste(icon, (int(icon_x), int(y_main + 4)), icon) 
                else:   
                    draw.rounded_rectangle(
                    [(x_main  - 20, y_main - 20), (x_main + QUEST_BOX_LENGTH, y_main + QUEST_BOX_HEIGHT)],
                    fill=(40, 39, 50), outline="black", width=3, radius=20
                    )
                # Draw text
                draw.text((x_main + QUEST_TXT_X_POSITION, y_main + QUEST_TXT_Y_POSITION_M), text, fill="white", font=font)
                draw.text((x_main + QUEST_TXT_X_POSITION, y_main + QUEST_TXT_Y_POSITION), text2, fill="white", font=font2)
                
                
                # Update vertical position for the next quest
                y_main += text_gap
            
            # Render Side Quests on the right
            for i, quest in enumerate(self.sideQ.keys()):
                if i == self.QUEST_LIMIT:
                    break  # Limit to 4 side quests
                
                des = self.sideQ[quest]
                text,text2 = cut_text(quest,des)

                # Draw icon (aligned to the right)
                if quest == self.tracked_item:
                    draw.rounded_rectangle(
                        [(x_side - 20, y_side - 20), (x_side + QUEST_BOX_LENGTH, y_side + QUEST_BOX_HEIGHT)],
                        fill=(40, 39, 50), outline=self.TRACKING_COLOR, width=3, radius=20
                    )
                    icon_x = x_side   # Adjust icon position relative to the text
                    img.paste(icon, (int(icon_x), int(y_side + 4)), icon)
                
                else:
                # Draw rounded rectangle for side quest
                    draw.rounded_rectangle(
                        [(x_side - 20, y_side - 20), (x_side + QUEST_BOX_LENGTH, y_side + QUEST_BOX_HEIGHT)],
                        fill=(40, 39, 50), outline="black", width=3, radius=20
                    )
                
                
                # Draw text (aligned to the right)
                draw.text((x_side + QUEST_TXT_X_POSITION , y_side + QUEST_TXT_Y_POSITION_M ), text, fill="white", font=font)
                draw.text((x_side + QUEST_TXT_X_POSITION, y_side+ QUEST_TXT_Y_POSITION), text2, fill="white", font=font2)
                
                
                
                # Update vertical position for the next quest
                y_side += text_gap
            
            # Save the output image
            output_path = OUTPUT_IMG_PATH
            img.save(output_path)
            return output_path
        
        except Exception as e:
            error_trace = traceback.format_exc()
            QMessageBox.critical(self, "Error", f"Failed to generate image: {e} {error_trace}")

    def set_wallpaper_windows(self, image_path):
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(basedir,image_path), 3)
            QMessageBox.information(self, "Success", "Wallpaper set successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set wallpaper: {e}")

    def set_wallpaper_linux(self, image_path):
        try:
            ## print(f"gsettings set org.gnome.desktop.background picture-uri-dark {os.path.join(basedir,image_path)}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri {os.path.join(basedir,image_path)}")
            os.system(f"gsettings set org.gnome.desktop.background picture-uri-dark {os.path.join(basedir,image_path)}")
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
            # print(output_image)
            self.set_wallpaper(output_image)


def main():
    app = QApplication(sys.argv)
    window = WallpaperApp()
    app.setWindowIcon(QtGui.QIcon(ICON_PATH))
    window.resize(1000, 800)  # Adjust window size
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
