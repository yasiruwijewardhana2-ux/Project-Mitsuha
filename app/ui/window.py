import time

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt, QTimer

from app.config import (
    APP_CONFIG,
    Expression,
    VisualMode,
)

from app.robot.robot import Robot
from app.core.renderer import RobotEyeRenderer
from app.core.serial_controller import SerialController


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_CONFIG.WINDOW_TITLE)
        self.resize(
            APP_CONFIG.WINDOW_WIDTH,
            APP_CONFIG.WINDOW_HEIGHT,
        )

        self.setStyleSheet(
            f"background-color: rgb{APP_CONFIG.BG_COLOR};"
        )

        self.robot = Robot()

        self.renderer = RobotEyeRenderer(self.robot)

        self.setCentralWidget(self.renderer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._main_loop)
        self.timer.start(
            int(1000 / APP_CONFIG.TARGET_FPS)
        )

        self.last_time = time.time()

        self.serial_thread = SerialController()
        self.serial_thread.start()

        self.robot.expr_manager.set_expression(
            Expression.EXCITED
        )
          def _main_loop(self):
        now = time.time()

        dt = min(now - self.last_time, 0.033)

        self.last_time = now

        self.robot.update(dt)

        self.renderer.update()


    def keyPressEvent(self, event):
        key = event.key()

        keys_to_expr = {
            Qt.Key_1: Expression.HAPPY,
            Qt.Key_2: Expression.ANGRY,
            Qt.Key_3: Expression.SAD,
            Qt.Key_4: Expression.THINKING,
            Qt.Key_5: Expression.SLEEPING,
            Qt.Key_6: Expression.CHARGING,
            Qt.Key_7: Expression.LISTENING,
            Qt.Key_8: Expression.EXCITED,
            Qt.Key_9: Expression.NEUTRAL,
            Qt.Key_Q: Expression.LOVE,
            Qt.Key_W: Expression.CONFUSED,
            Qt.Key_E: Expression.LAUGHING,
        }

        if key in keys_to_expr:
            self.robot.expr_manager.set_expression(
                keys_to_expr[key]
            )

        elif key == Qt.Key_B:
            self.robot.blink()

        elif key == Qt.Key_C:
            self.robot.is_cyclops = not self.robot.is_cyclops

            self.robot.expr_manager.set_expression(
                self.robot.expr_manager.current_expression
            )

        elif key == Qt.Key_V:
            modes = list(VisualMode)

            index = modes.index(
                self.robot.effects.visual_mode
            )

            self.robot.effects.visual_mode = modes[
                (index + 1) % len(modes)
            ]

        elif key == Qt.Key_Left:
            self.robot.look_at(-35, 0)

        elif key == Qt.Key_Right:
            self.robot.look_at(35, 0)

        elif key == Qt.Key_Up:
            self.robot.look_at(0, -35)

        elif key == Qt.Key_Down:
            self.robot.look_at(0, 35)
              def keyPressEvent(self, event):
        key = event.key()

        keys_to_expr = {
            Qt.Key_1: Expression.HAPPY,
            Qt.Key_2: Expression.ANGRY,
            Qt.Key_3: Expression.SAD,
            Qt.Key_4: Expression.THINKING,
            Qt.Key_5: Expression.SLEEPING,
            Qt.Key_6: Expression.CHARGING,
            Qt.Key_7: Expression.LISTENING,
            Qt.Key_8: Expression.EXCITED,
            Qt.Key_9: Expression.NEUTRAL,
            Qt.Key_Q: Expression.LOVE,
            Qt.Key_W: Expression.CONFUSED,
            Qt.Key_E: Expression.LAUGHING,
        }

        if key in keys_to_expr:
            self.robot.expr_manager.set_expression(keys_to_expr[key])

        elif key == Qt.Key_B:
            self.robot.blink()

        elif key == Qt.Key_C:
            self.robot.is_cyclops = not self.robot.is_cyclops
            self.robot.expr_manager.set_expression(
                self.robot.expr_manager.current_expression
            )

        elif key == Qt.Key_V:
            modes = list(VisualMode)
            index = modes.index(self.robot.effects.visual_mode)
            self.robot.effects.visual_mode = modes[(index + 1) % len(modes)]

        elif key == Qt.Key_Left:
            self.robot.look_at(-35, 0)

        elif key == Qt.Key_Right:
            self.robot.look_at(35, 0)

        elif key == Qt.Key_Up:
            self.robot.look_at(0, -35)

        elif key == Qt.Key_Down:
            self.robot.look_at(0, 35)

    def closeEvent(self, event):
        self.serial_thread.stop()
        super().closeEvent(event)
