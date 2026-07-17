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
