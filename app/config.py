from dataclasses import dataclass
from typing import Tuple, Dict
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


class Emotion(Enum):
    """The 20 core emotions from docs/021_Emotion_System.md. This is
    Mitsuha's *internal* emotional state, tracked by the Emotion Engine
    (CompanionCore) -- richer than what the face can actually display.

    EMOTION_TO_EXPRESSION below maps each of these down to one of the 15
    Expression values the eyes/animation system can render. Several
    emotions currently share an Expression because there's no dedicated
    visual for them yet (e.g. CURIOUS and FOCUSED both read as THINKING).
    If you want distinct looks for those later, that's a change to
    expressions.py's visual set, not to this mapping.
    """
    HAPPY = auto()
    CURIOUS = auto()
    CALM = auto()
    EXCITED = auto()
    THINKING = auto()
    CARING = auto()
    MOTIVATED = auto()
    FOCUSED = auto()
    SLEEPY = auto()
    RELAXED = auto()
    CONFUSED = auto()
    SURPRISED = auto()
    PLAYFUL = auto()
    PROUD = auto()
    SHY = auto()
    WORRIED = auto()
    PROTECTIVE = auto()
    LISTENING = auto()
    GREETING = auto()
    LONELY = auto()


# Best-effort mapping until dedicated visuals exist for every emotion.
EMOTION_TO_EXPRESSION: Dict[Emotion, Expression] = {
    Emotion.HAPPY: Expression.HAPPY,
    Emotion.CURIOUS: Expression.THINKING,
    Emotion.CALM: Expression.NEUTRAL,
    Emotion.EXCITED: Expression.EXCITED,
    Emotion.THINKING: Expression.THINKING,
    Emotion.CARING: Expression.LOVE,
    Emotion.MOTIVATED: Expression.EXCITED,
    Emotion.FOCUSED: Expression.THINKING,
    Emotion.SLEEPY: Expression.TIRED,
    Emotion.RELAXED: Expression.NEUTRAL,
    Emotion.CONFUSED: Expression.CONFUSED,
    Emotion.SURPRISED: Expression.SURPRISED,
    Emotion.PLAYFUL: Expression.LAUGHING,
    Emotion.PROUD: Expression.HAPPY,
    Emotion.SHY: Expression.SAD,
    Emotion.WORRIED: Expression.SCARED,
    Emotion.PROTECTIVE: Expression.ANGRY,
    Emotion.LISTENING: Expression.LISTENING,
    Emotion.GREETING: Expression.HAPPY,
    Emotion.LONELY: Expression.SAD,
}

# Emotions that should make eye/look movement read as faster/livelier.
# Used by robot.py's mood_based_multiplier.
ENERGETIC_EMOTIONS = {
    Emotion.HAPPY, Emotion.EXCITED, Emotion.PLAYFUL,
    Emotion.MOTIVATED, Emotion.SURPRISED, Emotion.GREETING,
}


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
