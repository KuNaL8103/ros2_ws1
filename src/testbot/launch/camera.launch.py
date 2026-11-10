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
    share = get_package_share_directory('testbot')
    world = os.path.join(share, 'worlds', 'camera.sdf')

    gz_args = LaunchConfiguration('gz_args')
    image_view = LaunchConfiguration('image_view')

    # the normal testbot bringup: gz, clock bridge, RSP, spawn, controllers
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    # gz.msgs.Image -> sensor_msgs/msg/Image, and the matching CameraInfo.
    # The [ means "Gazebo to ROS"; there is no closing bracket.
    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        output='screen',
    )

    # a simple ROS-side viewer; RViz can be used instead
    camera_viewer = Node(
        package='rqt_image_view',
        executable='rqt_image_view',
        arguments=['/camera/image_raw'],
        condition=IfCondition(image_view),
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'gz_args', default_value='-r ' + world,
            description="Gazebo args; append -s for a headless server"),
        DeclareLaunchArgument(
            'image_view', default_value='true',
            description='Open rqt_image_view on /camera/image_raw'),
        gazebo,
        camera_bridge,
        camera_viewer,
    ])
