import pyttsx3
import speech_recognition as sr
from PySide6.QtCore import QThread, Signal

class VoiceThread(QThread):
    text_received = Signal(str)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.running = True

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def run(self):
        self.speak("Ohayou Yasiru! I am ready.")
        recognizer = sr.Recognizer()
        
        while self.running:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                try:
                    # Mic එකෙන් අහන්න උත්සාහ කරනවා
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio)
                    if text:
                        self.text_received.emit(text) 
                        response = self.core.get_response(text)
                        self.speak(response)
                except Exception as e:
                    # Mic එකේ හෝ කතා කරන එකේ ප්‍රශ්නයක් වුණොත් මේක එනවා
                    continue
