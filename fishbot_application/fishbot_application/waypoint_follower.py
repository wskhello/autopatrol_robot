from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active() #等待导航系统激活
    goal_poses = []
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = nav.get_clock().now().to_msg()
    goal_pose.pose.position.x = 1.0
    goal_pose.pose.position.y = -1.0
    goal_pose.pose.position.z = 0.0
    goal_pose.pose.orientation.w = 1.0 #这是四元数的w分量，表示没有旋转

    goal_pose1 = PoseStamped()
    goal_pose1.header.frame_id = 'map'
    goal_pose1.header.stamp = nav.get_clock().now().to_msg()
    goal_pose1.pose.position.x = 0.0
    goal_pose1.pose.position.y = -1.0
    goal_pose1.pose.position.z = 0.0
    goal_pose1.pose.orientation.w = 1.0 #这是四元数的w分量，表示没有旋转

    goal_poses.append(goal_pose)
    goal_poses.append(goal_pose1)

    nav.followWaypoints(goal_poses) #发送导航目标点
    
     
    while not nav.isTaskComplete(): #等待导航完成
        feedback = nav.getFeedback() #获取导航反馈信息
        if feedback:
            nav.get_logger().info(f"剩余距离:{feedback.distance_remaining}") #打印导航反馈信息
    result = nav.getResult() #获取导航结果
    nav.get_logger().info(f"导航结果:{result}") #打印导航结果
   