# app/robot/autonomy/behavior_tree.py
from enum import Enum, auto
import random

# Node සහ Status classes මෙම ෆයිල් එකේම නිර්වචනය කර ඇති නිසා 
# අලුතින් import කරන්න අවශ්‍ය නැත.

class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

class Node:
    def tick(self, robot):
        raise NotImplementedError

class Selector(Node): # OR Logic
    def __init__(self, children): 
        self.children = children
    
    def tick(self, robot):
        for child in self.children:
            if child.tick(robot) != Status.FAILURE: 
                return Status.SUCCESS
        return Status.FAILURE

class IdleWanderNode(Node):
    """Randomly changes eye look target to simulate curiosity."""
    def tick(self, robot):
        if random.random() < 0.05: 
            target_x = random.uniform(-25, 25)
            target_y = random.uniform(-15, 15)
            robot.look_at(target_x, target_y)
            return Status.SUCCESS
        return Status.RUNNING

class ExpressionReactionNode(Node):
    """Trigger an expression if the robot is bored."""
    def tick(self, robot):
        # robot object එකේ ඉන්න expression manager එකට access කරන්න
        if hasattr(robot, '_idle_look_timer') and robot._idle_look_timer < -2.0:
            # මෙතනදී Expression එකක් trigger කරන්න පුළුවන්
            return Status.SUCCESS
        return Status.FAILURE