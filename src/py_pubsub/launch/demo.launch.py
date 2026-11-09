import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # pull in another launch file (here, the one in this same package)
    pubsub = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('py_pubsub'),
                'launch', 'pubsub.launch.py')
        )
    )

    # a plain shell-level command, run as a child process
    hz = ExecuteProcess(
        cmd=['ros2', 'topic', 'hz', '/topic'],
        output='screen',
    )

    return LaunchDescription([pubsub, hz])
