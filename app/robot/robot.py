import math
import random

from app.config import Expression, APP_CONFIG, AnimationPriority
from app.core.physics import SpringFloat
from app.core.animation import AnimationEngine
from app.robot.eye import Eye
from app.robot.expressions import ExpressionManager
from app.robot.effects import EffectsManager
from app.core.animation_manager import AnimationManager, AnimationTask

# අලුතින් එකතු කළ CompanionCore
from app.robot.companion_core import CompanionCore

# Imports for Behavior Tree
from app.robot.autonomy.behavior_tree import Selector, IdleWanderNode, ExpressionReactionNode

class Robot:
    def __init__(self):
        self.left_eye = Eye(is_left=True)
        self.right_eye = Eye(is_left=False)

        self.anim_engine = AnimationEngine()
        self.anim_manager = AnimationManager()
        
        # Companion Core එක initialize කරන්න
        self.companion = CompanionCore()
        
        # 2. Behavior Tree (Brain) - Nodes ඇතුලත් කිරීම
        self.brain = Selector([
            ExpressionReactionNode(),
            IdleWanderNode()
        ]) 

        self.expr_manager = ExpressionManager(
            self.anim_engine, self.left_eye, self.right_eye
        )

        self.effects = EffectsManager()
        self.spring_x = SpringFloat(tension=0.15, dampening=0.62)
        self.spring_y = SpringFloat(tension=0.15, dampening=0.62)

        self.breathe_offset = 0.0
        self.is_cyclops = False
        self._next_blink_timer = random.uniform(2.0, 5.0)
        self._idle_look_timer = random.uniform(1.0, 3.0)
        self._micro_saccade_timer = 0.2

    def sync_mood_to_expression(self):
        """Mood එක අනුව Expression එක ස්වයංක්‍රීයව වෙනස් කිරීම."""
        # මෙතන Expression Enum එකේ තියෙන නම් හරිද කියලා බලන්න (උදා: HAPPY, SAD, NEUTRAL)
        mood_map = {
            "HAPPY": Expression.HAPPY,
            "SUPPORTIVE": Expression.NEUTRAL,
            "BORED": Expression.SAD,
            "NEUTRAL": Expression.NEUTRAL
        }
        
        target_expr = mood_map.get(self.companion.mood, Expression.NEUTRAL)
        
        # දැනට තියෙන expression එක නෙවෙයි නම් විතරක් මාරු කරන්න
        if self.expr_manager.current_expression != target_expr:
            self.expr_manager.set_expression(target_expr)

    def update(self, dt):
        # Mood එක අනුව Expression එක Sync කරන්න
        self.sync_mood_to_expression()

        # Brain එකේ logic එක run කරන්න
        self.brain.tick(self)
        
        # Animation Manager එක update කරන්න
        self.anim_manager.update(dt)

        # Auto blink එක
        self._handle_auto_blink(dt)

        self.anim_engine.update(dt)
        self.effects.update(dt, self.expr_manager.current_expression)

        self.spring_x.update()
        self.spring_y.update()

        # Breathing logic
        if self.expr_manager.current_expression == Expression.SLEEPING:
            self.breathe_offset = math.sin(self.effects.pulse_time * 1.5) * 5.0
        else:
            self.breathe_offset = math.sin(self.effects.pulse_time * 3.0) * 1.5

    def _handle_auto_blink(self, dt):
        if self.expr_manager.current_expression in (
            Expression.SLEEPING,
            Expression.CHARGING,
        ):
            return

        self._next_blink_timer -= dt

        if self._next_blink_timer <= 0:
            self.blink()
            self._next_blink_timer = random.uniform(1.5, 5.0)

    def look_at(self, offset_x, offset_y):
        self.spring_x.target = offset_x
        self.spring_y.target = offset_y
        self._idle_look_timer = 4.0

    def blink(self, duration=APP_CONFIG.BLINK_DURATION):
        """
        Blink animation using the AnimationManager.
        """
        def perform_blink():
            def open_eyes():
                for is_left, eye in ((True, self.left_eye), (False, self.right_eye)):
                    targets = self.expr_manager.get_target_params(self.expr_manager.current_expression, is_left)
                    self.anim_engine.animate(eye, "top_lid", targets["top_lid"], duration, priority=AnimationPriority.HIGH)
                    self.anim_engine.animate(eye, "bottom_lid", targets["bottom_lid"], duration, priority=AnimationPriority.HIGH)

            for eye in (self.left_eye, self.right_eye):
                if eye == self.right_eye and self.is_cyclops: continue
                self.anim_engine.animate(eye, "top_lid", 1.0, duration / 2, priority=AnimationPriority.HIGH, on_complete=open_eyes if eye == self.left_eye else None)
                self.anim_engine.animate(eye, "bottom_lid", 0.0, duration / 2, priority=AnimationPriority.HIGH)

        self.anim_manager.add_task(AnimationTask(
            name="blink",
            priority=AnimationPriority.HIGH,
            action=perform_blink,
            duration=duration
        ))
