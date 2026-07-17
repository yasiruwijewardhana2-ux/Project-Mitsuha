import math
import random

from app.config import Expression, APP_CONFIG, AnimationPriority
from app.core.physics import SpringFloat
from app.core.animation import AnimationEngine
from app.robot.eye import Eye
from app.robot.expressions import ExpressionManager
from app.robot.effects import EffectsManager

# අලුතින් එකතු කළ import ටික
from app.core.animation_manager import AnimationManager
from app.robot.autonomy.behavior_tree import Selector

class Robot:
    def __init__(self):
        self.left_eye = Eye(is_left=True)
        self.right_eye = Eye(is_left=False)

        self.anim_engine = AnimationEngine()
        
        # 1. Animation Manager එක Init කරන්න
        self.anim_manager = AnimationManager()
        
        # 2. Behavior Tree (Brain) එක Init කරන්න
        self.brain = Selector([]) 

        self.expr_manager = ExpressionManager(
            self.anim_engine,
            self.left_eye,
            self.right_eye
        )

        self.effects = EffectsManager()
        self.spring_x = SpringFloat(tension=0.15, dampening=0.62)
        self.spring_y = SpringFloat(tension=0.15, dampening=0.62)

        self.breathe_offset = 0.0
        self.is_cyclops = False
        self._next_blink_timer = random.uniform(2.0, 5.0)
        self._idle_look_timer = random.uniform(1.0, 3.0)
        self._micro_saccade_timer = 0.2

    def update(self, dt):
        # 3. Brain එකේ logic එක run කරන්න
        self.brain.tick(self)
        
        # 4. Animation Manager එක update කරන්න
        self.anim_manager.update(dt)

        self._handle_auto_blink(dt)
        self._handle_biological_saccades(dt)

        self.anim_engine.update(dt)
        self.effects.update(dt, self.expr_manager.current_expression)

        self.spring_x.update()
        self.spring_y.update()

        # ... (ඔයාගේ ඉතිරි update logic එක මෙතනම තියෙන්න දෙන්න) ...
        if self.expr_manager.current_expression == Expression.SLEEPING:
            self.breathe_offset = math.sin(self.effects.pulse_time * 1.5) * 5.0
        else:
            self.breathe_offset = math.sin(self.effects.pulse_time * 3.0) * 1.5

    # ... (ඉතිරි methods ටික එහෙමම තියෙන්න දෙන්න) ...
    def _handle_auto_blink(self, dt):
        # ... (පැවති code එක) ...
        pass

    def _handle_biological_saccades(self, dt):
        # ... (පැවති code එක) ...
        pass

    def look_at(self, offset_x, offset_y):
        self.spring_x.target = offset_x
        self.spring_y.target = offset_y
        self._idle_look_timer = 4.0

    def blink(self, duration=APP_CONFIG.BLINK_DURATION):
        # ... (පැවති code එක) ...
        pass
