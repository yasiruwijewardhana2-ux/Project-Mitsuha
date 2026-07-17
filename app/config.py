from dataclasses import dataclass
from typing import Tuple
from enum import Enum, auto

class Expression(Enum):
    NEUTRAL = auto()
    HAPPY = auto()
    ANGRY = auto()
    SAD = auto()
    THINKING = auto()
    SLEEPING = auto()
    CHARGING = auto()
    LISTENING = auto()
    EXCITED = auto()
    SCARED = auto()
    SURPRISED = auto()
    CONFUSED = auto()
    LAUGHING = auto()
    TIRED = auto()
    LOVE = auto()

class VisualMode(Enum):
    OLED = auto()
    RGB = auto()
    NEON = auto()
    CYBERPUNK = auto()

class AnimationPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Config:
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 300
    WINDOW_TITLE = "Project Mitsuha - Vector Edition Engine"
    TARGET_FPS = 60

APP_CONFIG = Config()
