# app/robot/autonomy/behavior_tree.py
import random
from app.robot.autonomy.behavior_tree import Node, Status

class IdleWanderNode(Node):
    """Randomly changes eye look target to simulate curiosity."""
    def tick(self, robot) -> Status:
        # random.random() පාවිච්චි කරලා 5% probability එකක් දෙනවා
        if random.random() < 0.05: 
            target_x = random.uniform(-25, 25)
            target_y = random.uniform(-15, 15)
            robot.look_at(target_x, target_y)
            return Status.SUCCESS
        return Status.RUNNING

class ExpressionReactionNode(Node):
    """Trigger an expression if the robot is bored (idle for too long)."""
    def tick(self, robot) -> Status:
        # මෙතන logic එක දාන්න: උදා: 5 seconds එකක් හෙලවෙන්නේ නැත්නම් bored වෙනවා
        if robot._idle_look_timer < -2.0:
            robot.expr_manager.set_expression(Expression.THINKING)
            return Status.SUCCESS
        return Status.FAILURE
