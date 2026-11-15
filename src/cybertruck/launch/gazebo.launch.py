import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('cybertruck')
    world = os.path.join(share, 'worlds', 'cybertruck.sdf')
    xacro_file = os.path.join(share, 'urdf', 'cybertruck.urdf.xacro')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str)

    gz_args = LaunchConfiguration('gz_args')
    drive = LaunchConfiguration('drive')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '--ros-args',
            '-r', '/scan:=/scan_raw',
        ],
        output='screen',
    )

    # retag the scan frame from the scoped Gazebo name to lidar_link
    scan_frame_fix = Node(
        package='cybertruck',
        executable='scan_frame_fix',
        output='screen',
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
        output='screen',
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'cybertruck',
                   '-z', '0.01'],
        output='screen',
    )

    jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster',
                   '--controller-manager-timeout', '30'],
        output='screen',
    )

    diff_cont = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont',
                   '--controller-manager-timeout', '30'],
        output='screen',
    )

    cmd_vel = Node(
        package='cybertruck',
        executable='cmd_vel_publisher',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(drive),
        output='screen',
    )

    delayed_spawn = TimerAction(period=3.0, actions=[spawn])
    load_jsb = RegisterEventHandler(
        OnProcessExit(target_action=spawn, on_exit=[jsb]))
    load_diff = RegisterEventHandler(
        OnProcessExit(target_action=jsb, on_exit=[diff_cont]))

    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_args', default_value='-r ' + world,
            description="Gazebo args; append -s for a headless server"),
        DeclareLaunchArgument(
            'drive', default_value='true',
            description='Start the automatic circle-driving cmd_vel publisher'),
        gazebo,
        clock_bridge,
        scan_frame_fix,
        rsp,
        delayed_spawn,
        load_jsb,
        load_diff,
        cmd_vel,
    ])
