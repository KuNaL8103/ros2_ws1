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
    world = os.path.join(share, 'worlds', 'walls.sdf')
    slam_params = os.path.join(
        share, 'config', 'mapper_params_online_async.yaml')
    rviz_config = os.path.join(share, 'config', 'slam.rviz')

    gz_args = LaunchConfiguration('gz_args')
    rviz = LaunchConfiguration('rviz')

    # robot + Gazebo, but no automatic cmd_vel publisher: drive it yourself
    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={
            'gz_args': gz_args,
            'drive': 'false',
        }.items(),
    )

    # the official launch handles the lifecycle configure/activate steps
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'),
                         'launch', 'online_async_launch.py')),
        launch_arguments={
            'slam_params_file': slam_params,
            'use_sim_time': 'true',
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz),
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_args', default_value='-r ' + world,
            description='Gazebo args; append -s for a headless server'),
        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Open RViz with the map/LaserScan displays'),
        robot,
        slam,
        rviz_node,
    ])
