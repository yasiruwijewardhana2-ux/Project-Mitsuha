import math
import random

from app.config import Expression, APP_CONFIG, AnimationPriority, Emotion, EMOTION_TO_EXPRESSION, ENERGETIC_EMOTIONS
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

# --- Tunable constants (move to APP_CONFIG when convenient) ---
MAX_DT = 0.1                    # clamp dt so lag spikes don't jerk the springs/animations

# Micro-saccades: fast, tiny, near-constant eye jitter (reads as "alive/focused")
SACCADE_JITTER_RANGE = 2.5
SACCADE_INTERVAL_MIN = 0.1
SACCADE_INTERVAL_MAX = 0.3

# Idle glances: occasional bigger, brief look-away-and-back, layered on top
# of whatever the behavior tree/owner has set as the base gaze. This is
# separate from IdleWanderNode (which decides *where the robot is generally
# looking*) -- glances are short reflexive flicks, not a change of intent.
GLANCE_CHANCE_INTERVAL_MIN = 2.5
GLANCE_CHANCE_INTERVAL_MAX = 6.0
GLANCE_PROBABILITY = 0.35       # not every interval triggers a glance
GLANCE_RANGE = 12.0
GLANCE_HOLD_TIME = 0.4          # how long the glance offset lasts before decaying

BLINK_RATE_MIN = 1.5
BLINK_RATE_MAX = 5.0
DOUBLE_BLINK_CHANCE = 0.12      # occasional double-blink for realism


class Robot:
    def __init__(self, companion=None):
        self.left_eye = Eye(is_left=True)
        self.right_eye = Eye(is_left=False)

        self.anim_engine = AnimationEngine()
        self.anim_manager = AnimationManager()

        # Accept a shared CompanionCore from the caller (e.g. window.py's
        # `core`, which VoiceThread also uses) instead of always creating a
        # fresh one. Previously Robot() silently made its own CompanionCore,
        # completely disconnected from whatever instance actually handled
        # chat/voice replies -- so mood updates from real conversations never
        # reached the face at all. Falls back to creating one if none is
        # passed, so Robot() still works standalone (e.g. in tests).
        self.companion = companion if companion is not None else CompanionCore()

        self.brain = Selector([
            ExpressionReactionNode(),
            IdleWanderNode(),
        ])

        self.expr_manager = ExpressionManager(
            self.anim_engine, self.left_eye, self.right_eye
        )

        self.effects = EffectsManager()

        # Physics setup. A touch of overshoot (dampening < 1) makes eye
        # motion settle with a tiny bit of life instead of snapping dead-flat.
        # max_speed keeps a sudden big target change from whipping too fast.
        self.spring_x = SpringFloat(tension=0.15, dampening=0.62, max_speed=40.0)
        self.spring_y = SpringFloat(tension=0.15, dampening=0.62, max_speed=40.0)

        # --- Layered gaze model ---
        # base_look_*     : the "true" gaze target, set via look_at() by the
        #                   owner/behavior tree (e.g. IdleWanderNode, tracking
        #                   a face, reacting to touch, etc).
        # glance_offset_* : a short-lived reflexive flick added on top.
        # saccade jitter  : tiny near-constant twitch added on top of that.
        # Final spring target = base + glance + saccade, so none of these
        # systems permanently clobber each other (fixes the old drift bug
        # where saccades accumulated directly onto spring.target forever).
        self.base_look_x = 0.0
        self.base_look_y = 0.0
        self._glance_offset_x = 0.0
        self._glance_offset_y = 0.0
        self._glance_hold_timer = 0.0
        self._saccade_jitter_x = 0.0
        self._saccade_jitter_y = 0.0

        self.breathe_offset = 0.0
        self.is_cyclops = False

        # Timers
        self._next_blink_timer = random.uniform(BLINK_RATE_MIN, BLINK_RATE_MAX)
        self._idle_look_timer = random.uniform(GLANCE_CHANCE_INTERVAL_MIN, GLANCE_CHANCE_INTERVAL_MAX)

        # --- Life-like Movement Timers ---
        self._micro_saccade_timer = 0.2
        self.mood_based_multiplier = 1.0

    def _apply_mood_multiplier(self):
        """Faster eye movement for energetic/lively moods. This is purely
        derived/idempotent (safe to recompute every frame), unlike actual
        expression-setting -- which is owned exclusively by
        ExpressionReactionNode in the behavior tree now (edge-triggered on
        mood change) to avoid fighting manual/keyboard expression overrides.
        """
        current_mood = getattr(self.companion, "mood", Emotion.CALM)
        self.mood_based_multiplier = 1.5 if current_mood in ENERGETIC_EMOTIONS else 1.0

    def update(self, dt):
        # Clamp dt so a lag spike doesn't cause a visible jump/teleport
        dt = min(dt, MAX_DT)

        # Behavior tree nodes receive `robot` but not `dt` directly (brain.tick
        # only takes self) -- stash it here so timer-based nodes like
        # IdleWanderNode can read robot._last_dt instead of assuming 60fps.
        self._last_dt = dt

        # ExpressionReactionNode (in self.brain) is the sole owner of
        # mood -> expression sync, edge-triggered on actual mood changes.
        self.brain.tick(self)
        self._apply_mood_multiplier()

        self.anim_manager.update(dt)
        self._handle_auto_blink(dt)
        self.anim_engine.update(dt)
        self.effects.update(dt, self.expr_manager.current_expression)

        self._update_gaze(dt)

        # Breathing logic
        if self.expr_manager.current_expression == Expression.SLEEPING:
            self.breathe_offset = math.sin(self.effects.pulse_time * 1.5) * 5.0
        else:
            self.breathe_offset = math.sin(self.effects.pulse_time * 3.0) * 1.5

    def _update_gaze(self, dt):
        """Combine base gaze + idle glance + micro-saccade into the final
        spring target, then step the springs forward by dt."""
        # --- Idle glance: occasional short reflexive flick ---
        self._idle_look_timer -= dt
        if self._idle_look_timer <= 0:
            self._idle_look_timer = random.uniform(GLANCE_CHANCE_INTERVAL_MIN, GLANCE_CHANCE_INTERVAL_MAX)
            if random.random() < GLANCE_PROBABILITY:
                self._glance_offset_x = random.uniform(-GLANCE_RANGE, GLANCE_RANGE)
                self._glance_offset_y = random.uniform(-GLANCE_RANGE, GLANCE_RANGE)
                self._glance_hold_timer = GLANCE_HOLD_TIME

        if self._glance_hold_timer > 0:
            self._glance_hold_timer -= dt
            if self._glance_hold_timer <= 0:
                self._glance_offset_x = 0.0
                self._glance_offset_y = 0.0

        # --- Micro-saccade: tiny, near-constant twitch ---
        self._micro_saccade_timer -= dt
        if self._micro_saccade_timer <= 0:
            self._micro_saccade_timer = random.uniform(SACCADE_INTERVAL_MIN, SACCADE_INTERVAL_MAX)

            new_jitter_x = random.uniform(-SACCADE_JITTER_RANGE, SACCADE_JITTER_RANGE)
            new_jitter_y = random.uniform(-SACCADE_JITTER_RANGE, SACCADE_JITTER_RANGE)

            # Real micro-saccades are fast ballistic jumps, not smooth
            # eased motion. Feeding jitter through the spring like the rest
            # of the gaze meant the spring's damping (tuned for big, smooth
            # look-at moves) mostly cancelled it out before the next jitter
            # interval even arrived -- the eyes barely moved. Instead we
            # snap the jitter directly onto .value, and shift .target by the
            # same delta so the spring doesn't immediately try to pull the
            # snap back out.
            delta_x = new_jitter_x - self._saccade_jitter_x
            delta_y = new_jitter_y - self._saccade_jitter_y
            self.spring_x.value += delta_x
            self.spring_y.value += delta_y

            self._saccade_jitter_x = new_jitter_x
            self._saccade_jitter_y = new_jitter_y

        # Recompute the spring target fresh each frame from the three
        # layers -- nothing here permanently mutates base_look_*, so the
        # eyes always settle back to the true gaze target.
        self.spring_x.target = self.base_look_x + self._glance_offset_x + self._saccade_jitter_x
        self.spring_y.target = self.base_look_y + self._glance_offset_y + self._saccade_jitter_y

        self.spring_x.update(dt)
        self.spring_y.update(dt)

    def _handle_auto_blink(self, dt):
        if self.expr_manager.current_expression in (Expression.SLEEPING, Expression.CHARGING):
            return

        self._next_blink_timer -= dt
        if self._next_blink_timer <= 0:
            self.blink()

            # Occasional quick double-blink for realism.
            # AnimationTask has no "delay" field -- AnimationManager just
            # plays queued tasks back-to-back once the active one's duration
            # elapses. So instead of a delay, we queue a short no-op "gap"
            # task first, then the follow-up blink, which naturally spaces
            # the second blink out after the first one finishes.
            if random.random() < DOUBLE_BLINK_CHANCE:
                gap = 0.12
                self.anim_manager.add_task(AnimationTask(
                    name="double_blink_gap",
                    priority=AnimationPriority.HIGH,
                    action=lambda: None,
                    duration=gap,
                ))
                self.anim_manager.add_task(AnimationTask(
                    name="double_blink_followup",
                    priority=AnimationPriority.HIGH,
                    action=self.blink,
                    duration=APP_CONFIG.BLINK_DURATION,
                ))

            # Only roll a new random rate when we actually reset the timer,
            # not every single frame.
            self._next_blink_timer = random.uniform(BLINK_RATE_MIN, BLINK_RATE_MAX) / self.mood_based_multiplier

    def look_at(self, offset_x, offset_y):
        """Set the robot's true gaze target. Idle glances and micro-saccades
        will jitter around this point without permanently moving it."""
        self.base_look_x = offset_x
        self.base_look_y = offset_y

    def blink(self, duration=APP_CONFIG.BLINK_DURATION):
        # Proportional close/open, like a real blink: quick close, slightly
        # slower reopen. The old version closed in duration/2 but reopened
        # in a full extra `duration` -- inconsistent, and (combined with the
        # short default BLINK_DURATION) left only ~3 frames for the close
        # phase, too few for any easing to read as smooth.
        close_time = duration * 0.4
        open_time = duration * 0.6

        def perform_blink():
            def open_eyes():
                for is_left, eye in ((True, self.left_eye), (False, self.right_eye)):
                    targets = self.expr_manager.get_target_params(self.expr_manager.current_expression, is_left)
                    self.anim_engine.animate(eye, "top_lid", targets["top_lid"], open_time, priority=AnimationPriority.HIGH)
                    self.anim_engine.animate(eye, "bottom_lid", targets["bottom_lid"], open_time, priority=AnimationPriority.HIGH)

            for eye in (self.left_eye, self.right_eye):
                if eye == self.right_eye and self.is_cyclops:
                    continue
                self.anim_engine.animate(
                    eye, "top_lid", 1.0, close_time,
                    priority=AnimationPriority.HIGH,
                    on_complete=open_eyes if eye == self.left_eye else None,
                )
                self.anim_engine.animate(eye, "bottom_lid", 0.0, close_time, priority=AnimationPriority.HIGH)

        self.anim_manager.add_task(AnimationTask(
            name="blink",
            priority=AnimationPriority.HIGH,
            action=perform_blink,
            # Matches the real total visual time (close + open) now, so the
            # task queue doesn't consider the blink "done" while the eyes
            # are still mid-reopen.
            duration=close_time + open_time,
        ))
