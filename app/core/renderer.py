from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QPen,
    QTransform,
    QSurfaceFormat,
)
from PySide6.QtCore import Qt, QRectF

from app.config import APP_CONFIG, VisualMode
from app.robot.robot import Robot
from app.robot.eye import Eye

class RobotEyeRenderer(QOpenGLWidget):

    def __init__(self, robot: Robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        fmt = QSurfaceFormat()
        fmt.setSamples(8)
        fmt.setSwapInterval(1)
        self.setFormat(fmt)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(*APP_CONFIG.BG_COLOR))

        cx = self.width() / 2
        cy = self.height() / 2

        spacing = APP_CONFIG.EYE_SPACING if not self.robot.is_cyclops else 0
        gx = self.robot.spring_x.val
        gy = self.robot.spring_y.val

        # Draw Left Eye
        left_x = (
            cx if self.robot.is_cyclops else cx - spacing / 2
        ) + gx + self.robot.left_eye.offset_x
        
        left_y = cy + gy + self.robot.left_eye.offset_y + self.robot.breathe_offset

        self._draw_eye(painter, self.robot.left_eye, left_x, left_y)

        # Draw Right Eye
        if not self.robot.is_cyclops and self.robot.right_eye.scale_x > 0.05:
            right_x = cx + spacing / 2 + gx + self.robot.right_eye.offset_x
            right_y = cy + gy + self.robot.right_eye.offset_y + self.robot.breathe_offset
            self._draw_eye(painter, self.robot.right_eye, right_x, right_y)

        # Draw Cyberpunk Scanlines
        if self.robot.effects.visual_mode == VisualMode.CYBERPUNK:
            painter.setPen(QColor(0, 0, 0, 40))
            for y in range(0, self.height(), 4):
                painter.drawLine(0, y, self.width(), y)

    def _draw_eye(self, painter: QPainter, eye: Eye, cx: float, cy: float):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(eye.rotation)
        painter.scale(eye.scale_x, eye.scale_y)

        eye_path = QPainterPath()
        eye_path.addRoundedRect(
            QRectF(-eye.width / 2, -eye.height / 2, eye.width, eye.height),
            eye.radius,
            eye.radius,
        )

        # Handle Lids
        if eye.top_lid > 0:
            top_path = QPainterPath()
            lid_height = eye.height * eye.top_lid
            top_path.addRect(QRectF(-eye.width * 2, -eye.height, eye.width * 4, eye.height + (lid_height - eye.height / 2)))
            if eye.top_lid_angle != 0:
                transform = QTransform().translate(0, -eye.height / 2 + lid_height).rotate(eye.top_lid_angle).translate(0, eye.height / 2 - lid_height)
                top_path = transform.map(top_path)
            eye_path = eye_path.subtracted(top_path)

        if eye.bottom_lid > 0:
            bottom_path = QPainterPath()
            lid_height = eye.height * eye.bottom_lid
            bottom_path.addRect(QRectF(-eye.width * 2, eye.height / 2 - lid_height, eye.width * 4, eye.height))
            if eye.bottom_lid_angle != 0:
                transform = QTransform().translate(0, eye.height / 2 - lid_height).rotate(eye.bottom_lid_angle).translate(0, -eye.height / 2 + lid_height)
                bottom_path = transform.map(bottom_path)
            eye_path = eye_path.subtracted(bottom_path)

        r, g, b = self.robot.effects.current_color
        brightness = self.robot.effects.brightness

        if self.robot.effects.visual_mode == VisualMode.CYBERPUNK:
            painter.translate(-3, 0)
            painter.setBrush(QColor(int(255 * brightness), 0, 0, 140))
            painter.setPen(Qt.NoPen)
            painter.drawPath(eye_path)
            painter.translate(6, 0)
            painter.setBrush(QColor(0, int(150 * brightness), 255, 140))
            painter.drawPath(eye_path)
            painter.translate(-3, 0)
            base_color = QColor(int(255 * brightness), int(255 * brightness), int(255 * brightness), 220)
        else:
            base_color = QColor(int(r * brightness), int(g * brightness), int(b * brightness))

        if APP_CONFIG.ENABLE_BLOOM:
            painter.save()
            for i in range(1, APP_CONFIG.GLOW_INTENSITY + 1):
                glow = QColor(base_color)
                glow.setAlpha(150 // APP_CONFIG.GLOW_INTENSITY)
                pen = QPen(glow)
                pen.setWidthF(i * APP_CONFIG.GLOW_SPREAD)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(eye_path)
            painter.restore()

        painter.setPen(Qt.NoPen)
        painter.setBrush(base_color)
        painter.drawPath(eye_path)
        painter.restore()