import launch
import os
import launch_ros
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    #获取默认的urdf文件路径
    urdf_pkg_path = get_package_share_directory('fishbot_description')
    default_urdf_path = os.path.join(urdf_pkg_path,'urdf','fishbot','robot.urdf.xacro')

    #声明urdf目录的参数,方便修改
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value= str(default_urdf_path),
        description="加载的模型文件路径"
    )
    #通过文件路径获取内容,并转换成参数值对象,以供传入 robot_state_publisher

    #一个 substitution，运行时会执行括号里拼出来的 shell 命令
    #LaunchConfiguration('model')：读取 launch 参数 model 的值
    # Subsitions_command_result = launch.substitutions.Command(['cat ',launch.substitutions.LaunchConfiguration('model')])
    Subsitions_command_result = launch.substitutions.Command(['xacro ',launch.substitutions.LaunchConfiguration('model')])    
    #转换为参数值对象
    robot_description_value = launch_ros.parameter_descriptions.ParameterValue(Subsitions_command_result,value_type = str)

    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description':robot_description_value}]
        #parameters传递节点的参数
    )
    

    action_joint_state_publisher = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    action_rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        # arguments=['-d',default_rviz_config_path]
        #arguments相当于在命令行后加参数
    )


    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_robot_state_publisher, 
        action_joint_state_publisher,
        action_rviz_node

    ])