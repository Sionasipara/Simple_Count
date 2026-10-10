import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


def normalize(angle):
    """Wrap an angle to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


class ShapeDrawer(Node):
    def __init__(self):
        super().__init__('shape_drawer')

        # Parameters you can set from the command line
        self.declare_parameter('shape', 'square')
        self.declare_parameter('goal_x', 8.0)
        self.declare_parameter('goal_y', 3.0)
        self.declare_parameter('goal_theta', 1.57)
        self.shape = self.get_parameter('shape').value
        self.goal_x = self.get_parameter('goal_x').value
        self.goal_y = self.get_parameter('goal_y').value
        self.goal_theta = self.get_parameter('goal_theta').value

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.create_timer(0.02, self.control_loop)  # 50 Hz

        self.pose = None
        self.state = 'FORWARD'
        self.sides_done = 0
        self.start_x = None
        self.start_y = None
        self.target_heading = None
        self.start_time = None

        # Polygon / star settings
        if self.shape == 'square':
            self.num_sides, self.turn_angle, self.side_length = 4, math.pi / 2, 2.0
        elif self.shape == 'star':
            self.num_sides, self.turn_angle, self.side_length = 5, 4 * math.pi / 5, 3.0

        # Golden spiral settings: radius multiplies by phi every quarter turn
        self.w = 2.0                                   # rad/s, constant
        self.r0 = 0.05                                 # starting radius
        self.k = math.log((1 + math.sqrt(5)) / 2) / (math.pi / 2)

        self.get_logger().info(f'Drawing: {self.shape}')

    def pose_callback(self, msg):
        self.pose = msg

    def control_loop(self):
        if self.pose is None:
            return

        if self.shape in ('square', 'star'):
            cmd = self.polygon_step()
        elif self.shape == 'spiral':
            cmd = self.spiral_step()
        elif self.shape == 'goto':
            cmd = self.goto_step()
        else:
            self.get_logger().error('shape must be square, star, spiral or goto')
            raise SystemExit

        self.cmd_pub.publish(cmd)

    def finish(self):
        self.get_logger().info('Finished!')
        self.cmd_pub.publish(Twist())  # stop
        raise SystemExit

    # ---------- square and star ----------
    def polygon_step(self):
        cmd = Twist()
        if self.start_x is None:
            self.start_x, self.start_y = self.pose.x, self.pose.y
            self.target_heading = self.pose.theta

        if self.state == 'FORWARD':
            dist = math.hypot(self.pose.x - self.start_x, self.pose.y - self.start_y)
            if dist >= self.side_length:
                self.state = 'TURN'
                self.target_heading = normalize(self.target_heading + self.turn_angle)
            else:
                cmd.linear.x = 1.0

        elif self.state == 'TURN':
            error = normalize(self.target_heading - self.pose.theta)
            if abs(error) < 0.005:
                self.sides_done += 1
                if self.sides_done >= self.num_sides:
                    self.finish()
                self.state = 'FORWARD'
                self.start_x, self.start_y = self.pose.x, self.pose.y
            else:
                cmd.angular.z = max(min(4.0 * error, 1.5), -1.5)
        return cmd

    # ---------- golden spiral ----------
    def spiral_step(self):
        cmd = Twist()
        now = self.get_clock().now()
        if self.start_time is None:
            self.start_time = now
        t = (now - self.start_time).nanoseconds / 1e9

        margin = 0.5
        if not (margin < self.pose.x < 11.0 - margin and
                margin < self.pose.y < 11.0 - margin):
            self.finish()

        r = self.r0 * math.exp(self.k * self.w * t)   # radius at time t
        cmd.linear.x = self.w * r                      # v = w * r
        cmd.angular.z = self.w
        return cmd

    # ---------- go to an arbitrary pose ----------
    def goto_step(self):
        cmd = Twist()
        dx = self.goal_x - self.pose.x
        dy = self.goal_y - self.pose.y
        dist = math.hypot(dx, dy)

        if self.state == 'FORWARD':          # phase 1: drive to the point
            if dist < 0.05:
                self.state = 'TURN'
            else:
                err = normalize(math.atan2(dy, dx) - self.pose.theta)
                cmd.angular.z = 4.0 * err
                if abs(err) < 0.5:           # only drive once roughly facing the goal
                    cmd.linear.x = min(1.5 * dist, 2.0)

        elif self.state == 'TURN':           # phase 2: rotate to final orientation
            err = normalize(self.goal_theta - self.pose.theta)
            if abs(err) < 0.01:
                self.finish()
            cmd.angular.z = max(min(4.0 * err, 1.5), -1.5)
        return cmd


def main(args=None):
    rclpy.init(args=args)
    node = ShapeDrawer()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()