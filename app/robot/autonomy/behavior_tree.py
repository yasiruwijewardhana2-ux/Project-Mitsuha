from enum import Enum, auto
import random

class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

class Node:
    def tick(self, robot):
        raise NotImplementedError

class Selector(Node): 
    def __init__(self, children): 
        self.children = children
    
    def tick(self, robot):
        for child in self.children:
            if child.tick(robot) != Status.FAILURE: 
                return Status.SUCCESS
        return Status.FAILURE

class IdleWanderNode(Node):
    def tick(self, robot):
        # 5% chance to wander
        if random.random() < 0.05: 
            target_x = random.uniform(-25, 25)
            target_y = random.uniform(-15, 15)
            robot.look_at(target_x, target_y)
            return Status.SUCCESS
        return Status.RUNNING

class ExpressionReactionNode(Node):
    def tick(self, robot):
        # Boredom logic
        if hasattr(robot, '_idle_look_timer') and robot._idle_look_timer < -2.0:
            return Status.SUCCESS
        return Status.FAILURE