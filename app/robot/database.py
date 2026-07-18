import sqlite3
import datetime
import os
import threading


class DatabaseManager:
    """Mitsuha's local memory store (SQLite, on-device/PC-side for now).

    Tables:
      interactions       -- full conversation log, with speaker + optional
                             emotion tag, so history can be replayed in the
                             correct order/role for an LLM context window.
      user_data           -- simple key/value preferences (unchanged API).
      emotion_log         -- standalone emotion snapshots over time, even
                             outside of a specific message, so the Emotion
                             Engine can look back at recent mood trends
                             (e.g. "owner has seemed Stressed/Focused for a
                             while") independent of what was said.
    """

    def __init__(self, db_name="mitsuha_memory.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_name)

        # check_same_thread=False lets the voice thread and main thread both
        # touch the connection, but sqlite3 connections aren't inherently
        # safe for concurrent access from multiple threads at once -- this
        # lock serializes actual DB operations so writes from different
        # threads can't interleave and corrupt state.
        self._lock = threading.Lock()

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        with self._lock:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    speaker TEXT NOT NULL,      -- "yasiru" or "mitsuha"
                    message TEXT NOT NULL,
                    emotion TEXT                -- Mitsuha's emotion at the time, if known
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotion_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    reason TEXT                 -- brief note on what triggered it, if known
                )
            ''')
            self.conn.commit()

    # --- Conversation memory -------------------------------------------------

    def log_interaction(self, message, speaker="yasiru", emotion=None):
        """Log one turn of conversation. speaker should be "yasiru" or
        "mitsuha" so history can be reconstructed with correct roles."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock:
            self.cursor.execute(
                "INSERT INTO interactions (timestamp, speaker, message, emotion) VALUES (?, ?, ?, ?)",
                (timestamp, speaker, message, emotion),
            )
            self.conn.commit()

    def get_recent_interactions(self, limit=10):
        """Return the most recent interactions in chronological order, each
        as a dict: {timestamp, speaker, message, emotion}."""
        with self._lock:
            self.cursor.execute(
                "SELECT timestamp, speaker, message, emotion FROM interactions ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = self.cursor.fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_conversation_context(self, limit=10):
        """Return recent interactions formatted as LLM-style role messages:
        [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}, ...]
        Ready to drop straight into an LLM API call's messages list."""
        rows = self.get_recent_interactions(limit)
        role_map = {"mitsuha": "assistant"}
        return [
            {"role": role_map.get(row["speaker"], "user"), "content": row["message"]}
            for row in rows
        ]

    # --- Preferences -----------------------------------------------------

    def save_preference(self, key, value):
        with self._lock:
            self.cursor.execute(
                "REPLACE INTO user_data (key, value) VALUES (?, ?)", (key, value)
            )
            self.conn.commit()

    def get_preference(self, key, default=None):
        with self._lock:
            self.cursor.execute("SELECT value FROM user_data WHERE key = ?", (key,))
            result = self.cursor.fetchone()
        return result["value"] if result else default

    # --- Emotion history ---------------------------------------------------

    def log_emotion(self, emotion, reason=None):
        """Record a standalone emotion snapshot, independent of a specific
        message -- lets the Emotion Engine look at mood trends over time
        (e.g. sustained Focused/Worried state) rather than only reacting to
        the current instant."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock:
            self.cursor.execute(
                "INSERT INTO emotion_log (timestamp, emotion, reason) VALUES (?, ?, ?)",
                (timestamp, emotion, reason),
            )
            self.conn.commit()

    def get_recent_emotions(self, limit=20):
        """Return recent emotion snapshots, most recent last, as dicts."""
        with self._lock:
            self.cursor.execute(
                "SELECT timestamp, emotion, reason FROM emotion_log ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = self.cursor.fetchall()
        return [dict(row) for row in reversed(rows)]

    def get_dominant_recent_emotion(self, limit=10):
        """Simple mood-trend helper: the most frequent emotion among the
        last `limit` snapshots. Returns None if there's no history yet."""
        recent = self.get_recent_emotions(limit)
        if not recent:
            return None
        counts = {}
        for row in recent:
            counts[row["emotion"]] = counts.get(row["emotion"], 0) + 1
        return max(counts, key=counts.get)

    # --- Lifecycle -----------------------------------------------------

    def close(self):
        with self._lock:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
