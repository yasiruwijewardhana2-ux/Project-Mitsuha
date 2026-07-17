from app.robot.database import DatabaseManager

class CompanionCore:
    def __init__(self):
        self.db = DatabaseManager() # Database සම්බන්ධ කිරීම
        self.name = "Mitsuha"
        self.traits = ["kind", "supportive", "witty", "intelligent"]
        self.mood = "HAPPY"
        self.relationship_level = 0.5 

        # Database එකෙන් user ගේ නම තියෙනවද බලමු
        self.user_name = self.db.get_preference("user_name") or "Yasiru"

    def record_chat(self, message):
        """ඔයා කියන දේවල් database එකේ තියාගන්නවා."""
        self.db.log_interaction(message)

    def set_user_name(self, name):
        """ඔයාගේ නම මතක තියාගන්න."""
        self.user_name = name
        self.db.save_preference("user_name", name)

    def get_persona_prompt(self):
        """AI එකට දෙන්න ඕන කරන මූලික හැඳින්වීම (User ගේ නමත් එක්ක)."""
        return (f"You are {self.name}, a {', '.join(self.traits)} digital companion. "
                f"Your user's name is {self.user_name}. "
                "You are supportive with design and personal problems, but also witty and playful. "
                "Always be kind to your user.")

    def set_mood(self, mood):
        self.mood = mood
        print(f"Mitsuha's mood is now: {self.mood}")
