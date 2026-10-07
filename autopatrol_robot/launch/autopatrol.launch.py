import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.actions import TimerAction
from launch_ros.actions import Node
import os

def generate_launch_description():
    #获取路径
    autopatrol_robot_path = get_package_share_directory('autopatrol_robot')
    default_patrol_config_path = autopatrol_robot_path + '/config/patrol_config.yaml'

    action_patrol_node = launch_ros.actions.Node(
        package='autopatrol_robot', #功能包名
        executable='patrol_node',   #可执行文件名
        output='screen',            #日志输出
        parameters=[default_patrol_config_path],#参数
    )  

    # action_speaker_node = launch_ros.actions.Node(
    #     package='autopatrol_robot', #功能包名
    #     executable='speaker_node',   #可执行文件名
    #     output='screen',            #日志输出
    # )

    

    return launch.LaunchDescription([
        action_patrol_node,
        # action_speaker_node,
    ])