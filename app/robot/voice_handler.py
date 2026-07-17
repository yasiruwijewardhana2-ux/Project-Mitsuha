import pyttsx3
import speech_recognition as sr

class VoiceHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Voice එකේ වේගය සහ ශබ්දය පොඩ්ඩක් හදමු
        self.engine.setProperty('rate', 150) 
        self.engine.setProperty('volume', 1.0)

    def speak(self, text):
        print(f"Mitsuha: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except:
                return None
