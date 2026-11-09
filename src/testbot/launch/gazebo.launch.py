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
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('testbot')
    xacro_file = os.path.join(share, 'urdf', 'testbot.urdf.xacro')
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str)

    gz_args = LaunchConfiguration('gz_args')

    # 1. Gazebo Sim (Harmonic). -r = run immediately.
    #    Add -s for server-only (headless).
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    # Gazebo publishes its clock; bridge it so use_sim_time works in ROS
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    # 2. robot_state_publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
        output='screen',
    )

    # 3. spawn the model from the robot_description topic
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'testbot', '-z', '0.01'],
        output='screen',
    )

    # 4. joint_state_broadcaster
    jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster',
                   '--controller-manager-timeout', '30'],
        output='screen',
    )

    # 5. joint_trajectory_controller
    jtc = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller',
                   '--controller-manager-timeout', '30'],
        output='screen',
    )

    # the bicep-curl demo
    joint_publisher = Node(
        package='testbot',
        executable='joint_publisher',
        output='screen',
    )

    # give the Gazebo create service a moment to come up
    delayed_spawn = TimerAction(period=3.0, actions=[spawn])

    # spawn -> broadcaster -> trajectory controller, in that order
    load_jsb = RegisterEventHandler(
        OnProcessExit(target_action=spawn, on_exit=[jsb]))
    load_jtc = RegisterEventHandler(
        OnProcessExit(target_action=jsb, on_exit=[jtc]))

    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_args', default_value='-r empty.sdf',
            description="Gazebo args; use '-r -s empty.sdf' for headless"),
        gazebo,
        clock_bridge,
        rsp,
        delayed_spawn,
        load_jsb,
        load_jtc,
        joint_publisher,
    ])
