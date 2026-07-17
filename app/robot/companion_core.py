import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.robot.database import DatabaseManager

# .env ෆයිල් එක load කිරීම
load_dotenv()

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
        else:
            genai.configure(api_key=api_key)
            
        # Gemini Model එක සෙට් කිරීම (වේගවත් සහ කාර්යක්ෂම gemini-1.5-flash භාවිතය)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def record_chat(self, sender, message):
        """චැට් එක ඩේටාබේස් එකේ සේව් කිරීම (User: ... හෝ Mitsuha: ...)"""
        formatted_message = f"{sender}: {message}"
        self.db.log_interaction(formatted_message)

    def set_user_name(self, name):
        self.user_name = name
        self.db.save_preference("user_name", name)

    def get_persona_prompt(self):
        """Mitsuha ගේ පෞරුෂත්වය (Persona) අර්ථ දක්වන ප්‍රොම්ප්ට් එක"""
        return (f"You are {self.name}, a {', '.join(self.traits)} digital companion. "
                f"Your user's name is {self.user_name}. "
                "You are supportive with design and personal problems, but also witty and playful. "
                "Keep your answers friendly, somewhat concise, and always stay in character. "
                "Always respond in the language the user speaks to you (Sinhala or English).")

    def get_response(self, user_message):
        """පරණ මෙමරිය සහ Gemini භාවිතයෙන් පිළිතුරු ලබා දෙන ප්‍රධාන Function එක"""
        # 1. User කියපු දේ ඩේටාබේස් එකේ සේව් කරනවා
        self.record_chat("User", user_message)
        
        # 2. පසුගිය මැසේජ් 8 ඩේටාබේස් එකෙන් ලබා ගැනීම
        recent_chats = self.db.get_recent_interactions(limit=8)
        chat_history_str = "\n".join(recent_chats)
        
        # 3. Gemini එකට දෙන ප්‍රොම්ප්ට් එක සැකසීම
        prompt = f"""
{self.get_persona_prompt()}

---
Recent Chat History:
{chat_history_str}
---

Respond to the user's latest message. Remember to speak directly to {self.user_name}.
"""
        try:
            # 4. Gemini එකෙන් උත්තරය ලබා ගැනීම
            response = self.model.generate_content(prompt)
            mitsuha_reply = response.text.strip()
            
            # 5. Mitsuha ගේ උත්තරයත් ඩේටාබේස් එකේ සේව් කරනවා
            self.record_chat("Mitsuha", mitsuha_reply)
            
            return mitsuha_reply
        except Exception as e:
            print(f"Error generating response: {e}")
            return "අයියෝ, මගේ මොළේ පොඩි අවුලක් ගියා! API Key එක හරිද කියලා පොඩ්ඩක් බලන්නකෝ."

    def set_mood(self, mood):
        self.mood = mood
        print(f"Mitsuha's mood is now: {self.mood}")
