# fixed_jarvis.py
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QLabel,
    QSizePolicy, QFrame, QPushButton, QHBoxLayout, QStackedWidget
)
from PyQt5.QtGui import QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QIcon, QPainter
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "HarzAI")

# Define paths
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Ensure temp directories and minimal files exist to avoid crashes
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)
# Minimal files (if not present) so timers/readers don't crash
for fname, default in [
    ("Mic.data", "False"),
    ("Status.data", ""),
    ("Responses.data", "")
]:
    fp = os.path.join(TempDirPath, fname)
    if not os.path.exists(fp):
        with open(fp, "w", encoding="utf-8") as _f:
            _f.write(default)


# Function to modify answers
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

# Function to modify queries
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = [
        "how", "what", "who", "where", "when", "why",
        "which", "whose", "whom", "can you", "what's",
        "where's", "how's"
    ]

    if any(word + " " in new_query for word in query_words):
        if new_query and new_query[-1] not in ['.', '?', '!']:
            new_query += "?"
    else:
        if new_query and new_query[-1] not in ['.', '?', '!']:
            new_query += "."

    return new_query.capitalize()

# Function to set microphone status
def SetMicrophoneStatus(Command):
    with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding='utf-8') as file:
        file.write(Command)
def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = os.path.join(GraphicsDirPath, Filename)
    return Path

def TempDirectoryPath(Filename):
    Path = os.path.join(TempDirPath, Filename)
    return Path

# Function to get microphone status
def GetMicrophoneStatus():
    try:
        with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding='utf-8') as file:
            Status = file.read()
        return Status
    except:
        return "False"

# Function to set assistant status
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

# Function to get assistant status
def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "r", encoding='utf-8') as file:
            Status = file.read()
        return Status
    except:
        return "Available..."

# Function to show text on screen
def ShowTextToScreen(Text):
    with open(os.path.join(TempDirPath, "Responses.data"), "w", encoding="utf-8") as file:
        file.write(Text)


# ChatSection class
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(10)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        # PyQt5 supports Qt.NoTextInteraction
        self.chat_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction) # No text interaction
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setStretch(0, 1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Use QColor with hex for safety
        text_color = QColor("#4FC3F7")
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        # GIF label
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        gif_path = os.path.join(GraphicsDirPath, 'Jarvis.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size_W = 480
            max_gif_size_H = 270
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            # fallback pixmap
            self.gif_label.setText("")  # no gif available
        layout.addWidget(self.gif_label)

        # right aligned small status label under the gif
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: 30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        # timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.LoadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)  # Adjusted timer interval

        # install event filter - widget is a QObject so it's fine, but implement eventFilter
        self.chat_text_edit.viewport().installEventFilter(self)

        # Custom scrollbar styling via stylesheet placed on widget
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

            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
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

    # eventFilter to safely accept being an event filter target
    def eventFilter(self, obj, event):
        # placeholder, do not swallow events unless necessary
        return False

    def LoadMessages(self):
        global old_chat_message

        try:
            # Read the messages from the file
            with open(os.path.join(TempDirPath, "Responses.data"), "r", encoding='utf-8') as file:
                messages = file.read().strip()  # Strip whitespace for cleaner comparison

            # Initialize old_chat_message if not already set
            if 'old_chat_message' not in globals():
                old_chat_message = ""

            # Skip if the message has not changed or is empty
            if messages and old_chat_message != messages:
                self.addMessage(message=messages, color='white')
                old_chat_message = messages  # Update old message

        except FileNotFoundError:
            # Already ensured file existence at startup, but keep safe
            pass
        except Exception as e:
            print(f"Error in LoadMessages: {e}")


    def SpeechRecogText(self):
        try:
            with open(os.path.join(TempDirPath, "Status.data"), "r", encoding="utf-8") as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception:
            # be silent if file missing
            self.label.setText("")

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            # ensure attribute exists
            if not hasattr(self, "icon_label"):
                self.icon_label = QLabel()
            self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        # Track toggled state on self
        if not hasattr(self, "toggled"):
            self.toggled = True

        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Using QApplication.desktop() is fine in PyQt5 if QApplication exists before this class is constructed.
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            gif_label.setMovie(movie)
            # reasonable scaled height
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            movie.start()
        else:
            gif_label.setText("")  # no gif found
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon_label = QLabel()
        pixmap_path = GraphicsDirectoryPath('Mic_off.png')
        if os.path.exists(pixmap_path):
            pixmap = QPixmap(pixmap_path)
            new_pixmap = pixmap.scaled(60, 60)
            self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)

        # don't try to force huge fixed size if screen dims are huge; use max constraints
        self.setMinimumHeight(min(screen_height, 900))
        self.setMinimumWidth(min(screen_width, 1600))
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)  # less spamming than 5 ms

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception:
            self.label.setText("")

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()

        label = QLabel("")
        layout.addWidget(label)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        # Prefer flexible sizing over forcing full-screen; keep responsive
        self.setMinimumHeight(min(screen_height, 900))
        self.setMinimumWidth(min(screen_width, 1600))


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)

        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText("Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText("Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color: white; color: black")

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color: white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")

        title_label = QLabel(" Harz AI")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)

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
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setCentralWidget(stacked_widget)

        # Set geometry (full-screen style)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Use exec_ for PyQt5 compatibility
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
