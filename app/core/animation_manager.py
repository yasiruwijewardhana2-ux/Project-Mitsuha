# app/core/animation_manager.py

from typing import Callable, List, Optional
from dataclasses import dataclass
from app.config import AnimationPriority 

@dataclass
class AnimationTask:
    name: str
    priority: AnimationPriority
    action: Callable[[], None]
    duration: float
    interruptible: bool = True
    on_complete: Optional[Callable] = None

class AnimationManager:
    def __init__(self):
        self.active_task: Optional[AnimationTask] = None
        self.queue: List[AnimationTask] = []
        self._elapsed: float = 0.0

    def add_task(self, task: AnimationTask):
        # Priority check: interrupt if new task is higher
        if self.active_task and self.active_task.interruptible:
            if task.priority.value > self.active_task.priority.value:
                self.active_task = None
        
        self.queue.append(task)
        self.queue.sort(key=lambda x: x.priority.value, reverse=True)

    def update(self, dt: float):
        if not self.active_task and self.queue:
            self.active_task = self.queue.pop(0)
            self.active_task.action()
            self._elapsed = 0.0

        if self.active_task:
            self._elapsed += dt
            if self._elapsed >= self.active_task.duration:
                if self.active_task.on_complete: self.active_task.on_complete()
                self.active_task = None