from app.config import APP_CONFIG

class Eye:
    def __init__(self, is_left: bool):
        self.is_left = is_left

        self.width = APP_CONFIG.EYE_WIDTH
        self.height = APP_CONFIG.EYE_HEIGHT
        self.radius = APP_CONFIG.EYE_RADIUS

        self.offset_x = 0.0
        self.offset_y = 0.0

        self.scale_x = 1.0
        self.scale_y = 1.0

        self.rotation = 0.0

        self.top_lid = 0.0
        self.top_lid_angle = 0.0

        self.bottom_lid = 0.0
        self.bottom_lid_angle = 0.0
