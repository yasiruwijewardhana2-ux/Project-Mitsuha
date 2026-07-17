import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv
from app.robot.database import DatabaseManager

# .env ෆයිල් එකේ absolute path එක සොයා ගැනීම (Bulletproof Method)
# app/robot/companion_core.py සිට ප්‍රධාන Project-Mitsuha ෆෝල්ඩරයට පියවර 3ක් පසුපසට
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / '.env'

# .env ෆයිල් එක හරියටම ලිපිනයෙන්ම load කිරීම
load_dotenv(dotenv_path=dotenv_path)

class CompanionCore:
    def __init__(self):
        self.db = DatabaseManager()
        self.name = "Mitsuha"
        self.traits = ["kind", "supportive", "witty", "intelligent"]
        self.mood = "HAPPY"
        self.relationship_level = 0.5 
        
        # Database එකෙන් user ගේ නම ගැනීම
        self.user_name = self.db.get_preference("user_name") or "Yasiru"
        
        # Gemini API එක Configure කිරීම
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY එක .env ෆයිල් එකේ නැහැ!")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def record_chat(self, sender, message):
        """චැට් එක ඩේටාබේස් එකේ සේව් කිරීම"""
        formatted_message = f"{sender}: {message}"
        self.db.log_interaction(formatted_message)

    def set_user_name(self, name):
        self.user_name = name
        self.db.save_preference("user_name", name)

    def get_persona_prompt(self):
        """Mitsuha ගේ Persona එක"""
        return (f"You are {self.name}, a {', '.join(self.traits)} digital companion. "
                f"Your user's name is {self.user_name}. "
                "You are supportive with design and personal problems, but also witty and playful. "
                "Keep your answers friendly, somewhat concise, and always stay in character. "
                "Always respond in the language the user speaks to you (Sinhala or English).")

    def get_response(self, user_message):
        """පිළිතුරු ලබා දෙන ප්‍රධාන Function එක"""
        self.record_chat("User", user_message)
        
        # පසුගිය මැසේජ් 8 ලබා ගැනීම
        recent_chats = self.db.get_recent_interactions(limit=8)
        chat_history_str = "\n".join(recent_chats)
        
        prompt = f"""
{self.get_persona_prompt()}

---
Recent Chat History:
{chat_history_str}
---

Respond to the user's latest message. Remember to speak directly to {self.user_name}.
"""
        if not self.client:
            return "අයියෝ, මගේ මොළේ පොඩි අවුලක් ගියා! .env ෆයිල් එකේ GEMINI_API_KEY එක සෙට් කරලා නෑ වගේ."
            
        try:
            # අලුත් SDK සහ අලුත්ම Gemini 2.5 flash මොඩලය භාවිතය
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            mitsuha_reply = response.text.strip()
            
            self.record_chat("Mitsuha", mitsuha_reply)
            return mitsuha_reply
        except Exception as e:
            print(f"Error generating response: {e}")
            return "අයියෝ, මගේ මොළේ පොඩි අවුලක් ගියා! API Key එක හරිද කියලා පොඩ්ඩක් බලන්නකෝ."

    def set_mood(self, mood):
        self.mood = mood
        print(f"Mitsuha's mood is now: {self.mood}")
