import os
import time
from gtts import gTTS
from PySide6.QtCore import QThread, Signal

class VoiceThread(QThread):
    text_received = Signal(str)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.running = True

    def speak(self, text):
        print(f"Mitsuha: {text}")
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        
        # Windows default player එකෙන් play කරනවා (කිසිම lib එකක් ඕන නෑ)
        os.startfile("response.mp3")
        
        # Audio එක ප්ලේ වෙන්න පොඩි වෙලාවක් දෙනවා
        time.sleep(3) 
        if os.path.exists("response.mp3"):
            os.remove("response.mp3")

    def run(self):
        self.speak("Ohayou Yasiru! I am ready.")
        # Mic එකේ අවුල නිසා, දානකම් තාවකාලිකව මෙතන input එකක් ගන්නවා
        while self.running:
            user_input = input("You (Type here): ")
            if user_input:
                self.text_received.emit(user_input)
                response = self.core.get_response(user_input)
                self.speak(response)
