from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    talker = Node(
        package='cpp_pubsub',
        executable='talker',
        name='minimal_publisher',
        output='screen',
        # same as: --ros-args -p timer_period:=1.0
        parameters=[{'timer_period': 1.0}],
    )

    listener = Node(
        package='cpp_pubsub',
        executable='listener',
        name='minimal_subscriber',
        output='screen',
    )

    return LaunchDescription([talker, listener])
