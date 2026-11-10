import os

from ament_index_python.packages import (
    PackageNotFoundError,
    get_package_prefix,
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    LogInfo,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('testbot')
    layout = os.path.join(share, 'config', 'two_joint_layout.xml')

    gz_args = LaunchConfiguration('gz_args')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    actions = [
        DeclareLaunchArgument(
            'gz_args', default_value='-r empty.sdf',
            description="Gazebo args; use '-r -s empty.sdf' for headless"),
        gazebo,
    ]

    # PlotJuggler is a GUI app installed outside this workspace. Check the
    # ament index, NOT PATH: the executable lives in lib/plotjuggler/ and is
    # only reachable through `ros2 run`, not `which`.
    try:
        get_package_prefix('plotjuggler')
        have_plotjuggler = True
    except PackageNotFoundError:
        have_plotjuggler = False

    if not have_plotjuggler:
        actions.append(LogInfo(msg=(
            'PlotJuggler is not installed. Install it with: '
            'sudo apt install ros-jazzy-plotjuggler-ros -y')))
    else:
        actions.append(Node(
            package='plotjuggler',
            executable='plotjuggler',
            arguments=['-l', layout],
            output='screen',
        ))

    return LaunchDescription(actions)
