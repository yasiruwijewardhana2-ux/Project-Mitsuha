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
    WINDOW_WIDTH: int = 400
    WINDOW_HEIGHT: int = 300
    WINDOW_TITLE: str = "Project Mitsuha - Vector Edition Engine"
    TARGET_FPS: int = 60

    EYE_WIDTH: float = 70.0
    EYE_HEIGHT: float = 90.0
    EYE_RADIUS: float = 35.0
    EYE_SPACING: float = 125.0

    BLINK_DURATION: float = 0.10
    EXPRESSION_TRANSITION_DURATION: float = 0.30

    BG_COLOR: Tuple[int, int, int] = (2, 2, 5)

    OLED_COLOR: Tuple[int, int, int] = (10, 190, 255)
    CYBERPUNK_COLOR_1: Tuple[int, int, int] = (0, 150, 255)
    CYBERPUNK_COLOR_2: Tuple[int, int, int] = (255, 50, 100)
    NEON_COLOR: Tuple[int, int, int] = (0, 255, 200)

    GLOW_INTENSITY: int = 12
    GLOW_SPREAD: float = 2.0
    ENABLE_BLOOM: bool = True


APP_CONFIG = Config()
