import pyttsx3
import speech_recognition as sr
import sounddevice as sd # අලුතින් add කළා

class VoiceHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        print(f"Mitsuha: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        # අපි sounddevice පාවිච්චි කරන්නේ microphone එක අල්ලගන්න
        recognizer = sr.Recognizer()
        print("Listening...")
        # මේක ඔයාගේ mic එකෙන් අහනවා
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                return recognizer.recognize_google(audio)
            except:
                return None
