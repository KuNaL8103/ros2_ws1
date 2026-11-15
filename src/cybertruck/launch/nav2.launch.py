import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('cybertruck')
    nav2_share = get_package_share_directory('nav2_bringup')

    world = os.path.join(share, 'worlds', 'walls.sdf')
    map_yaml = os.path.join(share, 'config', 'my_map.yaml')
    params_file = os.path.join(share, 'config', 'nav2_params.yaml')

    gz_args = LaunchConfiguration('gz_args')
    rviz = LaunchConfiguration('rviz')

    # robot + Gazebo (no automatic cmd_vel publisher)
    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={
            'gz_args': gz_args,
            'drive': 'false',
        }.items(),
    )

    # map_server + AMCL + planner/controller/BT/behaviors
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'slam': 'False',
            'use_localization': 'True',
            'map': map_yaml,
            'use_sim_time': 'true',
            'params_file': params_file,
            'autostart': 'True',
            'use_composition': 'True',
            'use_respawn': 'False',
        }.items(),
    )

    # Nav2 outputs Twist on /cmd_vel; the diff drive controller needs
    # TwistStamped on /diff_cont/cmd_vel.
    cmd_vel_relay = Node(
        package='cybertruck',
        executable='cmd_vel_relay',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    rviz_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, 'launch', 'rviz_launch.py')),
        condition=IfCondition(rviz),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_args', default_value='-r ' + world,
            description='Gazebo args; append -s for a headless server'),
        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Open the Nav2 RViz view'),
        robot,
        navigation,
        cmd_vel_relay,
        rviz_node,
    ])
