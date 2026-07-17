# robot/autonomy/behavior_tree.py
from enum import Enum, auto

class Status(Enum):
    SUCCESS = auto(); FAILURE = auto(); RUNNING = auto()

class Node:
    def tick(self, robot): raise NotImplementedError

class Selector(Node): # OR Logic
    def __init__(self, children): self.children = children
    def tick(self, robot):
        for child in self.children:
            if child.tick(robot) != Status.FAILURE: return Status.SUCCESS
        return Status.FAILURE

# මෙතනට පස්සේ ඔයාගේ custom nodes (Idle_Wander, Check_Battery, etc.) දාන්න පුළුවන්.
