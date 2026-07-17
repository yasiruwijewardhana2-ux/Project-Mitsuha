import time
from PySide6.QtCore import QThread, Signal

class SerialController(QThread):
    command_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True

        try:
            import serial
            self.serial_module = serial
        except ImportError:
            self.serial_module = None

    def run(self):
        while self.is_running:
            time.sleep(0.5)

    def stop(self):
        self.is_running = False
        self.wait()
