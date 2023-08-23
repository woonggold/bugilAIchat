import sys
import sqlite3
import random
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QLineEdit, QPushButton, QVBoxLayout, QWidget

class ChatBotApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # SQLite 데이터베이스 연결 및 기존 코드 유지
        self.conn = sqlite3.connect('knowledge_base.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                question TEXT UNIQUE)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY,
                question_id INTEGER,
                answer TEXT)''')

        self.conn.commit()

    def init_ui(self):
        self.setWindowTitle("씨발 존나 오래 걸리네 챗봇 개새끼")
        self.setGeometry(100, 100, 800, 600)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setGeometry(20, 20, 760, 400)

        self.input_line_edit = QLineEdit(self)
        self.input_line_edit.setGeometry(20, 440, 600, 30)

        self.send_button = QPushButton("Send", self)
        self.send_button.setGeometry(640, 440, 140, 30)
        self.send_button.clicked.connect(self.handle_send_button)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_browser)
        self.layout.addWidget(self.input_line_edit)
        self.layout.addWidget(self.send_button)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def handle_send_button(self):
        user_input = self.input_line_edit.text()

        if user_input.lower() == "종료":
            self.close()
        else:
            response = self.get_random_answer(user_input)

            # 사용자 입력과 챗봇 응답을 UI에 표시
            self.text_browser.append(f"사용자: {user_input}")
            self.text_browser.append(f"챗봇: {response}")

            self.input_line_edit.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot_app = ChatBotApp()
    chatbot_app.show()
    sys.exit(app.exec_())
