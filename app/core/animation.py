from dataclasses import dataclass
from typing import Any, List, Optional, Callable

from app.config import AnimationPriority
from app.core.physics import get_easing_func


@dataclass
class AnimTask:
    target_obj: Any
    property_name: str
    start_value: float
    end_value: float
    duration: float
    elapsed: float = 0.0
    easing: str = "ease_in_out_cubic"
    priority: AnimationPriority = AnimationPriority.NORMAL
    on_complete: Optional[Callable] = None
    is_finished: bool = False


class AnimationEngine:
    def __init__(self):
        self._active_tasks: List[AnimTask] = []

    def animate(
        self,
        target,
        prop,
        end_val,
        duration,
        easing="ease_in_out_cubic",
        priority=AnimationPriority.NORMAL,
        on_complete=None,
    ):
        start_val = getattr(target, prop, 0.0)

        for task in self._active_tasks[:]:
            if task.target_obj == target and task.property_name == prop:
                if priority.value >= task.priority.value:
                    self._active_tasks.remove(task)
                else:
                    return

        self._active_tasks.append(
            AnimTask(
                target,
                prop,
                start_val,
                end_val,
                max(0.001, duration),
                0.0,
                easing,
                priority,
                on_complete,
            )
        )

    def update(self, dt):
        for task in self._active_tasks:
            if task.is_finished:
                continue

            task.elapsed += dt

            t = task.elapsed / task.duration
            eased = get_easing_func(task.easing)(t)

            if task.elapsed >= task.duration:
                eased = 1.0
                task.is_finished = True

            # FIX: original had an unclosed paren and was missing the
            # "* eased" multiplication entirely, so this line never actually
            # interpolated -- it would have thrown a SyntaxError (or, if that
            # got lost in a copy/paste, silently produced wrong values).
            value = task.start_value + (task.end_value - task.start_value) * eased

            setattr(task.target_obj, task.property_name, value)

            if task.is_finished and task.on_complete:
                task.on_complete()

        self._active_tasks = [
            t for t in self._active_tasks
            if not t.is_finished
        ]
