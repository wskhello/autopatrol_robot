from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    nav = BasicNavigator()
    init_pose = PoseStamped()
    init_pose.header.frame_id = 'map'
    init_pose.header.stamp = nav.get_clock().now().to_msg()
    init_pose.pose.position.x = 0.0
    init_pose.pose.position.y = 0.0
    init_pose.pose.position.z = 0.0
    init_pose.pose.orientation.w = 1.0 #这是四元数的w分量，表示没有旋转
    nav.setInitialPose(init_pose)
    nav.waitUntilNav2Active() #等待导航系统激活
    rclpy.spin(nav) #保持节点运行，直到被手动关闭
    rclpy.shutdown()