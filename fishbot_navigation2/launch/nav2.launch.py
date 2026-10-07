import os
import launch
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory 
from launch.launch_description_sources import PythonLaunchDescriptionSource #用于加载其他launch文件

def generate_launch_description():
    #获取与拼接默认路径
    fishbot_navigation2_dir = get_package_share_directory('fishbot_navigation2')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    rviz_config_dir = os.path.join(nav2_bringup_dir,'rviz','nav2_default_view.rviz')

    #创建launch配置
    use_sim_time = launch.substitutions.LaunchConfiguration('use_sim_time',default='true')
    map_yaml_path = launch.substitutions.LaunchConfiguration('map',default=os.path.join(fishbot_navigation2_dir,'maps','room5.yaml'))
    nav2_pram_path = launch.substitutions.LaunchConfiguration('params_file',default=os.path.join(fishbot_navigation2_dir,'config','nav2_params.yaml'))

    return launch.LaunchDescription([
        #声明新的 Launch 参数
        launch.actions.DeclareLaunchArgument('use_sim_time',default_value=use_sim_time,description='使用仿真时间'),
        launch.actions.DeclareLaunchArgument('map',default_value=map_yaml_path,description='地图文件路径'),
        launch.actions.DeclareLaunchArgument('params_file',default_value=nav2_pram_path,description='导航参数文件路径'),

        #加载 nav2_bringup 包中的 bringup_launch.py 文件
        launch.actions.IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [nav2_bringup_dir,'/launch','/bringup_launch.py']),
            #使用 Launch 参数替换原有参数
            launch_arguments={'use_sim_time':use_sim_time,'map':map_yaml_path,'params_file':nav2_pram_path}.items()
        ),
        launch_ros.actions.Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d',rviz_config_dir],
            parameters=[{'use_sim_time':use_sim_time}],
            ),
    ])