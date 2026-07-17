import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from app.robot.database import DatabaseManager

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

class CompanionCore:
    def __init__(self):
        self.db = DatabaseManager()
        self.name = "Mitsuha"
        self.user_name = self.db.get_preference("user_name") or "Yasiru"
        
        # OpenAI Client setup
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_response(self, user_message):
        # OpenAI Chat completion call
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # මේක ලාබයි, හරිම වේගවත්
                messages=[
                    {"role": "system", "content": f"You are {self.name}, helpful and witty."},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"අයියෝ, OpenAI එකේ පොඩි අවුලක්: {e}"
