class MainWindow(QMainWindow):
    def __init__(self, core): # මෙතනට core එක එනවා
        super().__init__()
        self.core = core  # මෙතනින් ඒක save කරගන්න
        # ... අනිත් UI වැඩ ...
