import launch
import os
import launch_ros
import launch.launch_description_sources
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    #获取默认的urdf文件路径
    urdf_pkg_path = get_package_share_directory('fishbot_description')

    default_xacro_path = os.path.join(urdf_pkg_path,'urdf','fishbot','robot.urdf.xacro')

    default_gazebo_world_path=os.path.join(urdf_pkg_path,'world','custom_room5.world') 

    #声明urdf目录的参数,方便修改
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value= str(default_xacro_path),
        description="加载的模型文件路径"
    )
    #通过文件路径获取内容,并转换成参数值对象,以供传入 robot_state_publisher

    #一个 substitution，运行时会执行括号里拼出来的 shell 命令
    #LaunchConfiguration('model'):读取 launch 参数 model 的值
    Subsitions_command_result = launch.substitutions.Command(['xacro ',launch.substitutions.LaunchConfiguration('model')])  


    #转换为参数值对象
    robot_description_value = launch_ros.parameter_descriptions.ParameterValue(Subsitions_command_result,value_type = str)

    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description':robot_description_value}]
        #parameters传递节点的参数
    )
    
    gazebo_launch_path = os.path.join(
            get_package_share_directory('gazebo_ros'),
            'launch',
            'gazebo.launch.py',
            
    )   

    #因为 spawn_entity.py 是通过ros2 run gazebo_ros spawn_entity.py 启动的,也是一个节点
    action_spawn_entity = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        #通过话题传递
        arguments=['-topic','/robot_description','-entity','fishbot']
    )

    action_gazebo_node = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            gazebo_launch_path,
        ),
        launch_arguments=[('world',default_gazebo_world_path),('verbose','true')]
    )

    #添加自动装载控制器动作
    action_load_joint_state_controller = launch.actions.ExecuteProcess(
        cmd='ros2 control load_controller fishbot_joint_state_broadcaster --set-state active'.split(' '),
        output='screen'
    )
    # action_load_effort_controller = launch.actions.ExecuteProcess(
    #     cmd='ros2 control load_controller fishbot_effort_controller --set-state active'.split(' '),
    #     output='screen'
    # )

    action_load_diff_drive_controller = launch.actions.ExecuteProcess(
        cmd='ros2 control load_controller fishbot_diff_drive_controller --set-state active'.split(' '),
        output='screen'
    )

    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_robot_state_publisher, 
        action_spawn_entity,
        action_gazebo_node,

        # ROS 2 launch 中的事件处理逻辑
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_spawn_entity,
                on_exit=[action_load_joint_state_controller]
            )
        ),
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_load_joint_state_controller,
                on_exit=[action_load_diff_drive_controller]
            )
        ),
        # launch.actions.RegisterEventHandler(
        #     event_handler=launch.event_handlers.OnProcessExit(
        #         target_action=action_load_effort_controller,
        #         on_exit=[action_load_diff_drive_controller]
        #     )
        # )
    ])