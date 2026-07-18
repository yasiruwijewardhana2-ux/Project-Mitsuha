from typing import Dict

from app.config import Expression, APP_CONFIG
from app.core.animation import AnimationEngine
from app.robot.eye import Eye


class ExpressionManager:

    def __init__(self, anim_engine: AnimationEngine, left_eye: Eye, right_eye: Eye):

        self.anim_engine = anim_engine
        self.left_eye = left_eye
        self.right_eye = right_eye

        self.current_expression = Expression.NEUTRAL

    def get_target_params(self, expr: Expression, is_left: bool) -> Dict[str, float]:

        params = {
            "width": APP_CONFIG.EYE_WIDTH,
            "height": APP_CONFIG.EYE_HEIGHT,
            "radius": APP_CONFIG.EYE_RADIUS,
            "top_lid": 0.0,
            "top_lid_angle": 0.0,
            "bottom_lid": 0.0,
            "bottom_lid_angle": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "offset_y": 0.0,
            "rotation": 0.0,
        }

        sign = 1 if is_left else -1

        if expr == Expression.HAPPY:
            params.update({
                "bottom_lid": 0.4,
                "bottom_lid_angle": 15 * sign,
                "top_lid": 0.1,
                "scale_y": 0.9
            })

        elif expr == Expression.ANGRY:
            params.update({
                "top_lid": 0.4,
                "top_lid_angle": 25 * sign,
                "bottom_lid": 0.1,
                "scale_x": 0.95
            })

        elif expr == Expression.SAD:
            params.update({
                "top_lid": 0.3,
                "top_lid_angle": -20 * sign,
                "bottom_lid": 0.2,
                "offset_y": 10
            })

        elif expr == Expression.THINKING:
            params.update({
                "top_lid": 0.3 if is_left else 0.0,
                "bottom_lid": 0.1 if is_left else 0.0,
                "offset_y": -5,
                "width": APP_CONFIG.EYE_WIDTH * 0.9,
                "rotation": 10 * sign,
            })

        elif expr == Expression.SLEEPING:
            params.update({
                "top_lid": 0.95,
                "bottom_lid": 0.05,
            })

        elif expr == Expression.CHARGING:
            params.update({
                "top_lid": 0.8,
                "scale_y": 0.8,
            })

        elif expr == Expression.EXCITED:
            params.update({
                "scale_x": 1.15,
                "scale_y": 1.15,
                "bottom_lid": 0.2,
                "bottom_lid_angle": 10 * sign,
            })

        elif expr == Expression.CONFUSED:

            params.update({
                "top_lid": 0.2,
                "top_lid_angle": 15 * sign,
                "rotation": 15 * sign,
            })

            if not is_left:
                params.update({
                    "top_lid_angle": -5 * sign,
                    "scale_y": 0.8
                })

        elif expr == Expression.LISTENING:
            # Alert, attentive -- slightly widened and leaned in, no droop.
            params.update({
                "scale_x": 1.05,
                "scale_y": 1.05,
                "top_lid": 0.05,
                "offset_y": -2,
            })

        elif expr == Expression.SCARED:
            # Wide, tense eyes with worried, angled lower lids.
            params.update({
                "scale_x": 1.2,
                "scale_y": 1.2,
                "top_lid": 0.0,
                "bottom_lid": 0.15,
                "bottom_lid_angle": -10 * sign,
                "offset_y": -3,
            })

        elif expr == Expression.SURPRISED:
            # Fully wide open, minimal lids -- the "!" reaction.
            params.update({
                "scale_x": 1.3,
                "scale_y": 1.3,
                "top_lid": 0.0,
                "bottom_lid": 0.0,
                "offset_y": -5,
            })

        elif expr == Expression.LAUGHING:
            # Squinted crescent "^_^" eyes -- more extreme than HAPPY.
            params.update({
                "bottom_lid": 0.5,
                "bottom_lid_angle": 20 * sign,
                "top_lid": 0.5,
                "top_lid_angle": 15 * sign,
                "scale_y": 0.7,
            })

        elif expr == Expression.TIRED:
            # Heavy drooping lids, softer than full SLEEPING.
            params.update({
                "top_lid": 0.6,
                "bottom_lid": 0.15,
                "offset_y": 5,
                "scale_y": 0.85,
            })

        elif expr == Expression.LOVE:
            # Soft curved, gentle-smile eyes.
            params.update({
                "bottom_lid": 0.5,
                "bottom_lid_angle": 25 * sign,
                "top_lid": 0.15,
                "scale_x": 1.05,
                "scale_y": 0.85,
            })

        return params

    def set_expression(
        self,
        expr: Expression,
        duration: float = APP_CONFIG.EXPRESSION_TRANSITION_DURATION
    ):

        self.current_expression = expr

        easing = (
            "ease_out_elastic"
            if expr == Expression.EXCITED
            else "ease_in_out_cubic"
        )

        for is_left, eye in [
            (True, self.left_eye),
            (False, self.right_eye)
        ]:

            targets = self.get_target_params(expr, is_left)

            for prop, value in targets.items():
                self.anim_engine.animate(
                    eye,
                    prop,
                    value,
                    duration,
                    easing,
                )
