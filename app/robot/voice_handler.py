from gtts import gTTS
import pygame
import os
import speech_recognition as sr
from PySide6.QtCore import QThread, Signal

class VoiceThread(QThread):
    text_received = Signal(str)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        pygame.mixer.init()
        self.running = True

    def speak(self, text):
        print(f"Mitsuha: {text}")
        # text එක audio file එකක් විදිහට හදනවා
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        
        # Audio එක play කරනවා
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # වැඩේ ඉවර වුණාම file එක delete කරනවා
        os.remove("response.mp3")

    def run(self):
        self.speak("Ohayou Yasiru! I am ready to talk.")
        recognizer = sr.Recognizer()
        
        while self.running:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio)
                    if text:
                        self.text_received.emit(text)
                        response = self.core.get_response(text)
                        self.speak(response)
                except:
                    continue
