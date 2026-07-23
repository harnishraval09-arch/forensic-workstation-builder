from PySide6.QtWidgets import QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forensic Workstation Builder")
        self.setGeometry(100, 100, 800, 600)
        
        label = QLabel("Welcome to Forensic Workstation Builder!")
        label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        self.setCentralWidget(label)