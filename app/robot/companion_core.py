# app/robot/companion_core.py

class CompanionCore:
    def __init__(self):
        self.name = "Mitsuha"
        self.traits = ["kind", "supportive", "witty", "intelligent"]
        self.mood = "HAPPY"  # දවසේ ඕනෑම වෙලාවක ඇය ඉන්න මූඩ් එක
        self.relationship_level = 0.5  # 0.0 to 1.0 (ඔයා එක්ක තියෙන බැඳීම)

    def get_persona_prompt(self):
        """AI එකට දෙන්න ඕන කරන මූලික හැඳින්වීම."""
        return (f"You are {self.name}, a {', '.join(self.traits)} digital companion. "
                "You are supportive with design and personal problems, but also witty and playful. "
                "Always be kind to Yasiru.")

    def set_mood(self, mood):
        self.mood = mood
        print(f"Mitsuha's mood is now: {self.mood}")
