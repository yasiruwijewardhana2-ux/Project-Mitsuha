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

        painter.fillRect(
            self.rect(),
            QColor(*APP_CONFIG.BG_COLOR),
        )

        cx = self.width() / 2
        cy = self.height() / 2

        spacing = (
            APP_CONFIG.EYE_SPACING
            if not self.robot.is_cyclops
            else 0
        )

        gx = self.robot.spring_x.val
        gy = self.robot.spring_y.val

        left_x = (
            cx + gx
            if self.robot.is_cyclops
            else cx
            - spacing / 2
            + gx
            + self.robot.left_eye.offset_x
        )

        left_y = (
            cy
            + gy
            + self.robot.left_eye.offset_y
            + self.robot.breathe_offset
        )

        self._draw_eye(
            painter,
            self.robot.left_eye,
            left_x,
            left_y,
        )

        if (
            not self.robot.is_cyclops
            and self.robot.right_eye.scale_x > 0.05
        ):

            right_x = (
                cx
                + spacing / 2
                + gx
                + self.robot.right_eye.offset_x
            )

            right_y = (
                cy
                + gy
                + self.robot.right_eye.offset_y
                + self.robot.breathe_offset
            )

            self._draw_eye(
                painter,
                self.robot.right_eye,
                right_x,
                right_y,
            )

        if (
            self.robot.effects.visual_mode
            == VisualMode.CYBERPUNK
        ):
            painter.setPen(QColor(0, 0, 0, 40))

            for y in range(0, self.height(), 4):
                painter.drawLine(
                    0,
                    y,
                    self.width(),
                    y,
                )
