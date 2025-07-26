from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy, QTextEdit
)
from PyQt5.QtGui import QIcon, QPixmap, QMovie, QFont, QTextCharFormat, QTextBlockFormat, QPainter, QColor
from PyQt5.QtCore import Qt, QSize, QTimer

from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")

# Define directories
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# Answer cleanup function
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Add punctuation and capitalize query
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Write mic status
def SetMicrophoneStatus(Command):
    with open(rf"{TempDirPath}\Mic.data", "w", encoding='utf-8') as file:
        file.write(Command)

# Read mic status
def GetMicrophoneStatus():
    with open(rf"{TempDirPath}\Mic.data", "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

# Write assistant status
def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

# Read assistant status
def GetAssistantStatus():
    with open(rf"{TempDirPath}\Status.data", "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

# Disable mic (status: False)
def MicButtonInitialed():  # You could rename to `DisableMic`
    SetMicrophoneStatus("False")

# Enable mic (status: True)
def MicButtonClosed():  # You could rename to `EnableMic`
    SetMicrophoneStatus("True")

# Path builders
def GraphicsDirectoryPath(Filename):
    return rf"{GraphicsDirPath}\{Filename}"

def TempDirectoryPath(Filename):
    return rf"{TempDirPath}\{Filename}"

# Write text to display
def ShowTextToScreen(Text):
    with open(TempDirectoryPath("Responses.data"), "w", encoding='utf-8') as file:
        file.write(Text)
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()

        self.toggled = False  # Initialize toggle state
        self.icon_label = QLabel()  # Needed for load_icon
        self.gif_label = QLabel()   # Needed for layout

        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)

        self.label = QLabel("")
        self.label.setStyleSheet(
            "color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;"
        )
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)

        layout.addWidget(self.gif_label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            } 

            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical { 
                border: none;
                background: none;
                color: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message

        with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()

            if None == messages:
                pass

            elif len(messages) <= 1:
                pass

            elif str(old_chat_message) == str(messages):
                pass

            else:
                self.addmessage(message= messages, color ='White')
                old_chat_message = messages

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        text_format = QTextCharFormat()
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        text_format.setForeground(QColor(color))
        cursor.setCharFormat(text_format)
        cursor.setBlockFormat(block_format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        screen_width = geometry.width()
        screen_height = geometry.height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)

        # Calculate the max height for the GIF to fit within the screen width
        max_gif_size_H = int(screen_width / 16 * 9)
        
        # Instead of setScaledSize, scale the QPixmap directly
        pixmap = QPixmap(GraphicsDirectoryPath('Jarvis.gif'))
        scaled_pixmap = pixmap.scaled(screen_width, max_gif_size_H, Qt.KeepAspectRatio)

        # Set the scaled pixmap to the QLabel
        gif_label.setPixmap(scaled_pixmap)
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")

        # Add widgets to layout
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled



class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        screen_width = geometry.width()
        screen_height = geometry.height()

        layout = QVBoxLayout()

        label = QLabel("")  # Placeholder label
        layout.addWidget(label)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.current_screen = None
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton(" Home ")
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color: black")

        message_button = QPushButton(" Chat ")
        message_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color: black")

        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(QIcon(GraphicsDirectoryPath("Minimize2.png")))
        self.minimize_button.setStyleSheet("background-color:white")
        self.minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath("Close.png")))
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        layout.addWidget(line_frame)

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen      
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.stacked_widget = QStackedWidget(self)

        initial_screen = InitialScreen()
        message_screen = MessageScreen()

        self.stacked_widget.addWidget(initial_screen)
        self.stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        top_bar = CustomTopBar(self, self.stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(self.stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()