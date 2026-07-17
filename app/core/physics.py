import math

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))

class SpringFloat:
    def __init__(self, value=0.0, tension=0.14, dampening=0.60):
        self.val = value
        self.target = value
        self.velocity = 0.0
        self.tension = tension
        self.dampening = dampening

    def update(self):
        force = (self.target - self.val) * self.tension
        self.velocity = (self.velocity + force) * self.dampening
        self.val += self.velocity
        return self.val

def ease_in_out_cubic(t):
    t = clamp(t, 0.0, 1.0)
    return 4 * t**3 if t < 0.5 else 0.5 * ((2 * t) - 2)**3 + 1

def ease_out_elastic(t):
    t = clamp(t, 0.0, 1.0)
    if t in (0.0, 1.0):
        return t
    p = 0.3
    return (math.pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1)

def get_easing_func(name):
    easings = {
        "linear": lambda t: clamp(t, 0.0, 1.0),
        "ease_in_out_cubic": ease_in_out_cubic,
        "ease_out_elastic": ease_out_elastic,
    }
    return easings.get(name, easings["linear"])
