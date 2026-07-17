import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# .env එක load කරනවා
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

class CompanionCore:
    def __init__(self):
        # Groq එකට සම්බන්ධ වෙන්න ඕනේ විදිහ
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY") 
        )
        self.name = "Mitsuha"
        
        # ඔන්න මේක තමයි මදි වෙලා තිබ්බේ!
        self.mood = "NEUTRAL" 

    def get_response(self, user_message):
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": f"You are {self.name}, helpful and witty."},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"
