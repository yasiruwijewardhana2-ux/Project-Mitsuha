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
        
        self.companion = CompanionCore()
        
        self.brain = Selector([
            ExpressionReactionNode(),
            IdleWanderNode()
        ]) 

        self.expr_manager = ExpressionManager(
            self.anim_engine, self.left_eye, self.right_eye
        )

        self.effects = EffectsManager()
        
        # Physics setup
        self.spring_x = SpringFloat(tension=0.15, dampening=0.62)
        self.spring_y = SpringFloat(tension=0.15, dampening=0.62)

        self.breathe_offset = 0.0
        self.is_cyclops = False
        
        # Timers
        self._next_blink_timer = random.uniform(2.0, 5.0)
        self._idle_look_timer = random.uniform(1.0, 3.0)
        
        # --- NEW: Life-like Movement Timers ---
        self._micro_saccade_timer = 0.2
        self.mood_based_multiplier = 1.0

    def sync_mood_to_expression(self):
        # AttributeError එක වළක්වා ගැනීමට getattr පාවිච්චි කරන්න
        current_mood = getattr(self.companion, 'mood', 'NEUTRAL')
        
        mood_map = {
            "HAPPY": Expression.HAPPY,
            "SUPPORTIVE": Expression.NEUTRAL,
            "BORED": Expression.SAD,
            "NEUTRAL": Expression.NEUTRAL
        }
        
        target_expr = mood_map.get(current_mood, Expression.NEUTRAL)
        
        if self.expr_manager.current_expression != target_expr:
            self.expr_manager.set_expression(target_expr)
            
        # Mood එක අනුව ඇස් වල වේගය වෙනස් කරන්න (Happy නම් වේගවත්)
        self.mood_based_multiplier = 1.5 if current_mood == "HAPPY" else 1.0

    def update(self, dt):
        self.sync_mood_to_expression()
        self.brain.tick(self)
        self.anim_manager.update(dt)
        self._handle_auto_blink(dt)
        self.anim_engine.update(dt)
        self.effects.update(dt, self.expr_manager.current_expression)

        # --- NEW: Micro-Saccades (ජීවමාන චලනය) ---
        self._micro_saccade_timer -= dt
        if self._micro_saccade_timer <= 0:
            # ඇස් වලට ඉතාම සියුම් චලනයක් එකතු කිරීම
            jitter_x = random.uniform(-1.0, 1.0)
            jitter_y = random.uniform(-1.0, 1.0)
            self.spring_x.target += jitter_x
            self.spring_y.target += jitter_y
            self._micro_saccade_timer = random.uniform(0.1, 0.3) # 0.1s - 0.3s අතර වේගයෙන්

        self.spring_x.update()
        self.spring_y.update()

        # Breathing logic
        if self.expr_manager.current_expression == Expression.SLEEPING:
            self.breathe_offset = math.sin(self.effects.pulse_time * 1.5) * 5.0
        else:
            self.breathe_offset = math.sin(self.effects.pulse_time * 3.0) * 1.5

    def _handle_auto_blink(self, dt):
        if self.expr_manager.current_expression in (Expression.SLEEPING, Expression.CHARGING):
            return

        # Mood එක අනුව blink rate එක වෙනස් කිරීම
        blink_rate = random.uniform(1.5, 5.0) / self.mood_based_multiplier
        
        self._next_blink_timer -= dt
        if self._next_blink_timer <= 0:
            self.blink()
            self._next_blink_timer = blink_rate

    def look_at(self, offset_x, offset_y):
        self.spring_x.target = offset_x
        self.spring_y.target = offset_y

    def blink(self, duration=APP_CONFIG.BLINK_DURATION):
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
