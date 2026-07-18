import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

from app.config import Emotion
from app.robot.database import DatabaseManager

# .env එක load කරනවා
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

# Canned, in-character fallback lines used when the LLM is unreachable
# (no API key, network down, request failed). Per the project's own
# offline-resiliency goal, Mitsuha should never speak a raw exception --
# she should stay in character even when the cloud brain is unavailable.
OFFLINE_FALLBACKS = [
    "Hmm, I can't quite reach my thoughts right now -- my connection's acting up.",
    "Give me a second... I'm having trouble thinking clearly right now.",
    "I heard you, but my mind's a bit foggy at the moment. Try again in a bit?",
]

_EMOTION_NAMES = {e.name for e in Emotion}


class CompanionCore:
    """Mitsuha's Emotion Engine + conversational brain.

    Every reply is tagged with one of the 20 core emotions (see
    app/config.py Emotion enum, per docs/021_Emotion_System.md). That
    emotion becomes self.mood (an Emotion enum member), which robot.py
    reads to drive facial expression and eye-movement energy, and is also
    logged to the emotion history table so mood trends can be tracked
    over time.
    """

    def __init__(self, db: DatabaseManager = None, history_limit: int = 8):
        api_key = os.getenv("GROQ_API_KEY")
        self.available = bool(api_key)
        if not self.available:
            print("[CompanionCore] WARNING: GROQ_API_KEY not set -- running in offline fallback mode.")

        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key or "missing",
        )
        self.name = "Mitsuha"
        self.history_limit = history_limit

        # Own our memory connection unless one is passed in, so other parts
        # of the app (e.g. window.py) can share a single DatabaseManager
        # instance if they want to.
        self.db = db if db is not None else DatabaseManager()

        # Emotion Engine state. CALM is the resting baseline -- there's no
        # explicit "neutral" in the 20-emotion doc, so CALM fills that role.
        self.mood = Emotion.CALM

    def _system_prompt(self):
        return (
            f"You are {self.name}, a warm, witty AI companion robot. You are grounded, "
            "supportive, and genuinely care about the person you're talking to -- not a "
            "generic assistant. Keep replies short and conversational (1-3 sentences), "
            "like something you'd actually say out loud, since your reply will be spoken.\n\n"
            "After your reply, on a new line, tag the single emotion that best matches your "
            "own reaction to this exchange. Choose exactly one from this list: "
            f"{', '.join(sorted(_EMOTION_NAMES))}.\n\n"
            "Respond in EXACTLY this format, nothing else:\n"
            "REPLY: <your spoken reply>\n"
            "EMOTION: <one emotion name from the list>"
        )

    def _parse_response(self, raw_text):
        """Pull REPLY/EMOTION out of the model's formatted output. Falls
        back gracefully if the model didn't follow the format exactly,
        rather than crashing on a malformed response."""
        reply_match = re.search(r"REPLY:\s*(.+?)(?:\n|$)", raw_text, re.IGNORECASE | re.DOTALL)
        emotion_match = re.search(r"EMOTION:\s*(\w+)", raw_text, re.IGNORECASE)

        reply = reply_match.group(1).strip() if reply_match else raw_text.strip()
        # Clean up in case REPLY captured trailing EMOTION line via DOTALL
        reply = re.split(r"\n?EMOTION:", reply, flags=re.IGNORECASE)[0].strip()

        emotion = Emotion.CALM
        if emotion_match:
            name = emotion_match.group(1).strip().upper()
            if name in _EMOTION_NAMES:
                emotion = Emotion[name]

        return reply, emotion

    def get_response(self, user_message):
        # Always log what the user said, even if we can't respond -- memory
        # of the conversation shouldn't depend on the API being up.
        self.db.log_interaction(user_message, speaker="yasiru")

        if not self.available:
            reply = self._offline_reply()
            self.mood = Emotion.WORRIED
            self.db.log_interaction(reply, speaker="mitsuha", emotion=self.mood.name)
            self.db.log_emotion(self.mood.name, reason="offline mode, no API key")
            return reply

        try:
            history = self.db.get_conversation_context(limit=self.history_limit)
            messages = [{"role": "system", "content": self._system_prompt()}]
            messages.extend(history)
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
            )
            raw_text = response.choices[0].message.content
            reply, emotion = self._parse_response(raw_text)

            self.mood = emotion
            self.db.log_interaction(reply, speaker="mitsuha", emotion=emotion.name)
            self.db.log_emotion(emotion.name, reason="conversation reply")
            return reply

        except Exception as e:
            # Never speak the raw exception out loud -- log it for
            # debugging, but keep Mitsuha in character for the user.
            print(f"[CompanionCore] get_response error: {e}")
            reply = self._offline_reply()
            self.mood = Emotion.WORRIED
            self.db.log_interaction(reply, speaker="mitsuha", emotion=self.mood.name)
            self.db.log_emotion(self.mood.name, reason=f"API error: {e}")
            return reply

    def _offline_reply(self):
        import random
        return random.choice(OFFLINE_FALLBACKS)
