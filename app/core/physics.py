"""
Core physics primitives for MitsuhaOS animation.

SpringFloat is a critically-tunable damped spring used to drive smooth,
lifelike motion (eye look-at, lids, head tilt, etc). It is frame-rate
independent: pass the real delta-time (seconds) into update(dt) every
tick and the motion will look the same whether you're running at 30fps,
60fps, or a laggy 12fps.
"""

import math


class SpringFloat:
    """A 1D damped spring that smoothly chases a target value.

    Usage:
        spring = SpringFloat(tension=0.15, dampening=0.62)
        spring.target = 10.0
        spring.update(dt)          # call every frame with real delta-time
        current = spring.value

    Parameters
    ----------
    tension: float
        How strongly the spring pulls toward the target. Higher = snappier.
        Roughly analogous to stiffness. Sane range: 0.05 - 0.4.
    dampening: float
        How quickly oscillation settles. 1.0 = fully damped (no bounce).
        Lower values (e.g. 0.5-0.8) allow a little lively overshoot/wobble
        before settling, which reads as more "alive" for eye motion.
    max_speed: float | None
        Optional hard clamp on velocity (units/second). Prevents a big,
        sudden target change (e.g. a snapped look_at) from producing an
        unnaturally fast whip-motion. None disables clamping.
    """

    # Sub-stepping keeps the integration stable/consistent even when dt
    # spikes (lag, tab switch, etc). Internally we always integrate in
    # fixed-size slices no larger than MAX_STEP seconds.
    MAX_STEP = 1.0 / 60.0

    def __init__(self, initial_value=0.0, tension=0.15, dampening=0.62, max_speed=None):
        self.value = float(initial_value)
        self.target = float(initial_value)
        self.velocity = 0.0

        self.tension = tension
        self.dampening = dampening
        self.max_speed = max_speed

    def update(self, dt):
        """Advance the spring simulation by dt seconds."""
        if dt <= 0:
            return

        # Break large/variable dt into fixed-size substeps so behavior is
        # consistent regardless of frame rate, and never numerically unstable
        # even if dt is unexpectedly large (e.g. after a stutter).
        remaining = dt
        while remaining > 0:
            step = min(self.MAX_STEP, remaining)
            self._integrate(step)
            remaining -= step

    def _integrate(self, dt):
        # Semi-implicit (symplectic) Euler integration: update velocity
        # first, then use the *new* velocity to update position. This is
        # noticeably more stable than naive Euler for spring systems and
        # is what most game engines use for this kind of motion.
        force = (self.target - self.value) * self.tension
        self.velocity = (self.velocity + force) * self.dampening

        if self.max_speed is not None:
            self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))

        # Normalize velocity application against a 60fps baseline tension/
        # dampening feel, scaled by actual dt, so tuning stays consistent.
        self.value += self.velocity * (dt * 60.0)

    def snap(self, value):
        """Instantly jump to a value with zero velocity (no spring fling)."""
        self.value = float(value)
        self.target = float(value)
        self.velocity = 0.0

    def is_settled(self, tolerance=0.01):
        """True once the spring has essentially reached its target and
        stopped moving -- useful for gating 'idle' behaviors."""
        return abs(self.target - self.value) < tolerance and abs(self.velocity) < tolerance

    def __repr__(self):
        return f"SpringFloat(value={self.value:.3f}, target={self.target:.3f}, velocity={self.velocity:.3f})"


class SpringVector2:
    """Convenience wrapper: two independent SpringFloats bundled as (x, y).
    Handy for eye look-at or head position where you want to set/read both
    axes together instead of managing spring_x / spring_y separately.
    """

    def __init__(self, initial_x=0.0, initial_y=0.0, tension=0.15, dampening=0.62, max_speed=None):
        self.x = SpringFloat(initial_x, tension, dampening, max_speed)
        self.y = SpringFloat(initial_y, tension, dampening, max_speed)

    @property
    def value(self):
        return (self.x.value, self.y.value)

    @property
    def target(self):
        return (self.x.target, self.y.target)

    @target.setter
    def target(self, xy):
        self.x.target, self.y.target = xy

    def update(self, dt):
        self.x.update(dt)
        self.y.update(dt)

    def snap(self, x, y):
        self.x.snap(x)
        self.y.snap(y)

    def is_settled(self, tolerance=0.01):
        return self.x.is_settled(tolerance) and self.y.is_settled(tolerance)


def _linear(t):
    return t


def _ease_in_quad(t):
    return t * t


def _ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)


def _ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2


def _ease_in_cubic(t):
    return t * t * t


def _ease_out_cubic(t):
    return 1 - pow(1 - t, 3)


def _ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def _ease_in_sine(t):
    return 1 - math.cos((t * math.pi) / 2)


def _ease_out_sine(t):
    return math.sin((t * math.pi) / 2)


def _ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


def _ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def _ease_out_elastic(t):
    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def _ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


_EASING_FUNCTIONS = {
    "linear": _linear,
    "ease_in_quad": _ease_in_quad,
    "ease_out_quad": _ease_out_quad,
    "ease_in_out_quad": _ease_in_out_quad,
    "ease_in_cubic": _ease_in_cubic,
    "ease_out_cubic": _ease_out_cubic,
    "ease_in_out_cubic": _ease_in_out_cubic,
    "ease_in_sine": _ease_in_sine,
    "ease_out_sine": _ease_out_sine,
    "ease_in_out_sine": _ease_in_out_sine,
    "ease_out_back": _ease_out_back,
    "ease_out_elastic": _ease_out_elastic,
    "ease_out_bounce": _ease_out_bounce,
}


def get_easing_func(name="linear"):
    """Look up a named easing function by string, e.g.
    get_easing_func("ease_out_cubic"). Each returned function takes a
    single float t in [0, 1] and returns the eased progress value.

    Falls back to linear if the name isn't recognized, rather than raising,
    so a typo'd easing name degrades gracefully instead of crashing an
    animation call.
    """
    if callable(name):
        # Already a function -- pass through unchanged.
        return name
    return _EASING_FUNCTIONS.get(name, _linear)


class PulseTimer:
    """Simple accumulating time source for sine-wave-driven effects
    (breathing, glow pulses, idle sway). Call update(dt) each frame and
    read .time, or use .wave() for a ready-made sine oscillator.
    """

    def __init__(self):
        self.time = 0.0

    def update(self, dt):
        self.time += dt

    def wave(self, speed=1.0, amplitude=1.0, phase=0.0):
        return math.sin(self.time * speed + phase) * amplitude
