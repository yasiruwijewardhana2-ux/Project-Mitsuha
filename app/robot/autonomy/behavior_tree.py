from enum import Enum, auto
import random

from app.config import Emotion, EMOTION_TO_EXPRESSION


class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class Node:
    def tick(self, robot):
        raise NotImplementedError


class Selector(Node):
    """Tries each child in order, stops at the first that isn't FAILURE.

    FIX: the original version collapsed RUNNING into SUCCESS
    (`if child.tick(robot) != Status.FAILURE: return Status.SUCCESS`),
    which silently lies about a still-in-progress child. That's harmless
    while nothing reads the Selector's own return value, but it breaks the
    moment you nest Selectors/Sequences or add anything that checks status
    meaningfully. This version reports RUNNING and SUCCESS distinctly.
    """

    def __init__(self, children):
        self.children = children

    def tick(self, robot):
        for child in self.children:
            status = child.tick(robot)
            if status == Status.RUNNING:
                return Status.RUNNING
            if status == Status.SUCCESS:
                return Status.SUCCESS
        return Status.FAILURE


class Sequence(Node):
    """Runs children in order, stops at the first FAILURE. All children
    must succeed for the Sequence to succeed. Not used by the current tree
    yet, but you'll want this shortly -- e.g. "detect touch" -> "look at
    owner" -> "play happy animation" is naturally a Sequence, not a
    Selector.
    """

    def __init__(self, children):
        self.children = children

    def tick(self, robot):
        for child in self.children:
            status = child.tick(robot)
            if status == Status.RUNNING:
                return Status.RUNNING
            if status == Status.FAILURE:
                return Status.FAILURE
        return Status.SUCCESS


class IdleWanderNode(Node):
    """Occasionally pick a new general look direction.

    FIX: the original rolled a 5% chance every single tick, which at
    60fps means ~3 direction changes per second -- far too twitchy, and it
    was fighting with robot.py's own idle-glance/micro-saccade layers for
    control of the eyes. This version uses an internal cooldown so it only
    even considers wandering every few seconds, matching the "idle
    micro-behaviors" pacing described in docs/022_Behavior_Tree.md.

    Division of labor with robot.py:
      - IdleWanderNode (here) decides *general gaze direction*, every few
        seconds.
      - robot.py's idle-glance system adds short reflexive flicks on top.
      - robot.py's micro-saccade system adds constant tiny jitter on top
        of that.
    None of the three should fight for the same job.
    """

    WANDER_INTERVAL_MIN = 4.0
    WANDER_INTERVAL_MAX = 9.0
    WANDER_PROBABILITY = 0.4  # not every eligible tick actually wanders

    def __init__(self):
        self._cooldown = random.uniform(self.WANDER_INTERVAL_MIN, self.WANDER_INTERVAL_MAX)

    def tick(self, robot):
        dt = getattr(robot, "_last_dt", 1.0 / 60.0)
        self._cooldown -= dt

        if self._cooldown > 0:
            return Status.RUNNING

        self._cooldown = random.uniform(self.WANDER_INTERVAL_MIN, self.WANDER_INTERVAL_MAX)

        if random.random() < self.WANDER_PROBABILITY:
            target_x = random.uniform(-25, 25)
            target_y = random.uniform(-15, 15)
            robot.look_at(target_x, target_y)
            return Status.SUCCESS

        return Status.RUNNING


class ExpressionReactionNode(Node):
    """Applies the Emotion Engine's current mood to the robot's face.

    FIX: the original node didn't actually react to anything -- it checked
    an unrelated idle-timer threshold that (given how robot.py resets that
    timer) could basically never be true, and even on "success" it had no
    effect at all. This version does the one job the name implies: read
    self.companion.mood (an Emotion, set by CompanionCore) and make sure
    the face matches it, using the same EMOTION_TO_EXPRESSION table the
    rest of the system uses.

    Note: this now overlaps with robot.py's own sync_mood_to_expression().
    Only one of them should own this responsibility long-term -- see the
    note left in robot.py. For now this node is a no-op SUCCESS if the
    expression already matches, so having both active isn't harmful, just
    slightly redundant.
    """

    def tick(self, robot):
        companion = getattr(robot, "companion", None)
        if companion is None:
            return Status.FAILURE

        mood = getattr(companion, "mood", None)
        if not isinstance(mood, Emotion):
            return Status.FAILURE

        target_expr = EMOTION_TO_EXPRESSION.get(mood)
        if target_expr is None:
            return Status.FAILURE

        if robot.expr_manager.current_expression != target_expr:
            robot.expr_manager.set_expression(target_expr)
            return Status.SUCCESS

        return Status.FAILURE
