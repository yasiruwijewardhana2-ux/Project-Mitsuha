import math
import random

from app.config import VisualMode, Expression, APP_CONFIG


class EffectsManager:

    def __init__(self):
        self.visual_mode = VisualMode.OLED
        self.current_color = APP_CONFIG.OLED_COLOR
        self.brightness = 1.0
        self.pulse_time = 0.0

    def update(self, dt, current_expression):

        self.pulse_time += dt

        if self.visual_mode == VisualMode.OLED:
            self.current_color = APP_CONFIG.OLED_COLOR

        elif self.visual_mode == VisualMode.NEON:
            self.current_color = APP_CONFIG.NEON_COLOR

        elif self.visual_mode == VisualMode.CYBERPUNK:
            self.current_color = APP_CONFIG.CYBERPUNK_COLOR_1

        if current_expression == Expression.CHARGING:
            self.brightness = 0.7 + 0.3 * math.sin(self.pulse_time * 3)

        elif current_expression == Expression.SLEEPING:
            self.brightness = 0.5 + 0.2 * math.sin(self.pulse_time * 1.5)

        elif current_expression == Expression.EXCITED:
            self.brightness = 0.9 + 0.1 * math.sin(self.pulse_time * 15)

        else:

            if random.random() < 0.05:
                self.brightness = random.uniform(0.95, 1.0)

            else:
                self.brightness += (1.0 - self.brightness) * 0.1
