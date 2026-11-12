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
    rviz_config = os.path.join(share, 'config', 'depth.rviz')

    gz_args = LaunchConfiguration('gz_args')
    rviz = LaunchConfiguration('rviz')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    # The rgbd_camera publishes image, depth_image, points and camera_info.
    # Remap to the names used in the lesson:
    #   /depth_camera/image_raw
    #   /depth_camera/depth/image_raw
    depth_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/depth_camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '--ros-args',
            '-r', '/depth_camera/image:=/depth_camera/image_raw',
            '-r', '/depth_camera/depth_image:=/depth_camera/depth/image_raw',
            '-r', '/depth_camera/points:=/depth_camera/points_raw',
        ],
        output='screen',
    )

    # Gazebo stamps the cloud with the optical frame but its coordinates are
    # in the link/sensor frame. Retag it so TF applies the optical rotation.
    cloud_frame_fix = Node(
        package='testbot',
        executable='depth_cloud_frame_fix',
        output='screen',
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
            description="Gazebo args; append -s for a headless server"),
        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Open RViz with the depth point cloud'),
        gazebo,
        depth_bridge,
        cloud_frame_fix,
        rviz_node,
    ])
