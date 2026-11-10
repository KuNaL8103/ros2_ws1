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
    rviz_config = os.path.join(share, 'config', 'lidar.rviz')

    gz_args = LaunchConfiguration('gz_args')
    rviz = LaunchConfiguration('rviz')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    # gz.msgs.LaserScan and gz.msgs.PointCloudPacked -> ROS 2.
    # gpu_lidar publishes the scan on <topic> and the cloud on <topic>/points.
    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/scan/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
        ],
        output='screen',
    )

    # Gazebo reports the sensor frame as the scoped name
    # testbot/head/lidar_sensor. Alias it to laser_link so RViz can
    # transform the scan using the URDF TF tree (the pose is identical).
    lidar_frame_alias = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--frame-id', 'laser_link',
                   '--child-frame-id', 'testbot/head/lidar_sensor'],
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
            description='Open RViz with the LaserScan display'),
        gazebo,
        lidar_bridge,
        lidar_frame_alias,
        rviz_node,
    ])
