import sys
from PySide6.QtWidgets import QApplication
from app.ui.window import MainWindow
from app.robot.companion_core import CompanionCore

def main():
    app = QApplication(sys.argv)
    
    # Core එක ඉන්නවා
    core = CompanionCore()
    
    # Window එකට core එක දෙනවා
    window = MainWindow(core)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
