# ros2_ws1

A ROS 2 **Jazzy** workspace of tutorial-style robot demos built with **RViz 2**,
**Gazebo Harmonic**, **ros2_control**, **slam_toolbox**, and **Nav2**.

The packages progress from minimal publisher/subscriber examples up to a
diff-drive Cybertruck that maps a walled world and navigates it autonomously.

---

## Requirements

- Ubuntu 24.04 (native or WSL 2)
- [ROS 2 Jazzy Jalisco](https://docs.ros.org/en/jazzy/Installation.html)
- Gazebo Harmonic (`gz sim`)

```bash
sudo apt install \
  ros-jazzy-ros-gz ros-jazzy-gz-ros2-control ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers ros-jazzy-slam-toolbox ros-jazzy-nav2-bringup \
  ros-jazzy-rqt-image-view ros-jazzy-xacro ros-jazzy-plotjuggler-ros
```

PlotJuggler is optional and only needed for the `testbot` plotting demo.

> The committed `build/`, `install/`, and `log/` directories were produced in
> WSL 2 (`/home/kunal/ros2_ws1`). Rebuild them on your own machine; do not rely
> on the checked-in artifacts.

---

## Workspace layout

```text
ros2_ws1/
├── src/
│   ├── cybertruck/        # diff-drive Cybertruck, SLAM + Nav2 demo
│   │   ├── config/        # controllers, Nav2 params, SLAM params, map, RViz
│   │   ├── launch/        # gazebo, slam, nav2
│   │   ├── src/           # cmd_vel_publisher, cmd_vel_relay, scan_frame_fix
│   │   ├── urdf/          # cybertruck.urdf.xacro
│   │   └── worlds/        # cybertruck.sdf, walls.sdf
│   ├── testbot/           # Tesla-bot upper body + camera/depth/lidar demos
│   │   ├── config/        # controllers, RViz configs, PlotJuggler layout
│   │   ├── launch/        # gazebo, camera, depth, lidar, plot
│   │   ├── src/           # joint_publisher, depth_cloud_frame_fix
│   │   ├── urdf/          # testbot.urdf.xacro
│   │   └── worlds/        # camera.sdf
│   ├── my_robot/          # xacro robot description + RViz demo
│   ├── r2d2/              # R2D2 description + animated state publisher
│   ├── cpp_pubsub/        # C++ talker/listener
│   ├── py_pubsub/         # Python talker/listener + launch composition
│   └── my_package/        # minimal "hello world" node
├── build/                 # colcon build output (generated)
├── install/               # colcon install space (generated)
├── log/                   # colcon logs (generated)
└── robot.urdf             # generated copy of my_robot's expanded URDF
```

`robot.urdf` is generated from `src/my_robot/urdf/robot.urdf.xacro`.
Edit the xacro, not the generated file.

---

## Packages

| Package        | Build type       | Summary                                                                                                                                            |
| -------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cybertruck` | `ament_cmake`  | 4.0 x 1.8 x 0.8 m rear-wheel-drive Cybertruck with a 2D lidar, driven by `diff_drive_controller` in Gazebo. Includes SLAM and Nav2 launch files. |
| `testbot`    | `ament_cmake`  | Fixed-base "Tesla-bot" upper body with two revolute arm joints, color camera, RGB-D camera, and lidar. Uses `joint_trajectory_controller`.       |
| `my_robot`   | `ament_cmake`  | Xacro-based robot with reusable macros (`robot_parts.xacro`), a gripper STL mesh, an RViz config, and a joint-slider demo.                       |
| `r2d2`       | `ament_python` | R2D2 URDF plus a node that animates four joints and broadcasts TF for RViz.                                                                        |
| `cpp_pubsub` | `ament_cmake`  | `talker` / `listener` on `std_msgs/msg/String` with a launch file.                                                                           |
| `py_pubsub`  | `ament_python` | Python `talker` / `listener`, plus a launch file that includes another launch file and runs `ros2 topic hz`.                                 |
| `my_package` | `ament_cmake`  | Scaffold package containing a single node that prints `hello world`.                                                                             |

---

## Build

From a clean shell:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws1

colcon build --symlink-install
source install/setup.bash
```

Build a single package while iterating:

```bash
colcon build --symlink-install --packages-select cybertruck
source install/setup.bash
```

Because `--symlink-install` is used, edits to Python, launch, URDF, and config
files take effect without rebuilding. C++ changes still require a rebuild.

---

## Demos

### 1. R2D2 in RViz

```bash
ros2 launch r2d2 demo.launch.py
```

In a second terminal, open the matching RViz layout:

```bash
ros2 run rviz2 rviz2 -d "$(ros2 pkg prefix r2d2)/share/r2d2/config/r2d2.rviz"
```

The `state_publisher` node animates the `l1_connect`, `l2_connect`, `tilt`,
and `periscope` joints and publishes the TF tree.

---

### 2. Articulated robot in RViz

```bash
ros2 launch my_robot demo.launch.py
```

Launch arguments:

| Argument | Default  | Effect                                                                        |
| -------- | -------- | ----------------------------------------------------------------------------- |
| `gui`  | `true` | Use `joint_state_publisher_gui` sliders; `false` publishes zero positions |
| `rviz` | `true` | Open `config/robot.rviz`                                                    |

Headless check of the description only:

```bash
ros2 launch my_robot demo.launch.py gui:=false rviz:=false
```

Regenerate the expanded URDF after editing the xacro:

```bash
xacro src/my_robot/urdf/robot.urdf.xacro > robot.urdf
```

---

### 3. testbot: ros2_control in Gazebo

Base simulation (empty world, arms curl every two seconds):

```bash
ros2 launch testbot gazebo.launch.py
```

Start Gazebo server-only (no GUI):

```bash
ros2 launch testbot gazebo.launch.py gz_args:="-r -s empty.sdf"
```

Other worlds and sensor demos:

```bash
ros2 launch testbot camera.launch.py    # /camera/image_raw in rqt_image_view
ros2 launch testbot depth.launch.py     # RGB-D point cloud in RViz
ros2 launch testbot lidar.launch.py     # LaserScan + PointCloud2 in RViz
ros2 launch testbot plot.launch.py      # PlotJuggler, elbow positions
```

`joint_publisher` publishes a `JointTrajectory` every 2 seconds to
`/joint_trajectory_controller/joint_trajectory`, alternately sending both
elbows to `+0.5` and `-0.5` rad. The controller chain is spawned in order:
`joint_state_broadcaster` then `joint_trajectory_controller`.

---

### 4. cybertruck: drive, SLAM, and Nav2

Drive a 1 m radius circle automatically:

```bash
ros2 launch cybertruck gazebo.launch.py
```

Spawn without the automatic driver and teleoperate:

```bash
ros2 launch cybertruck gazebo.launch.py drive:=false
# in another terminal
ros2 run cybertruck cmd_vel_relay
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

`cmd_vel_relay` is required because the Jazzy `diff_drive_controller` expects
`geometry_msgs/msg/TwistStamped` on `/diff_cont/cmd_vel`, while teleop and Nav2
publish a plain `Twist` on `/cmd_vel`.

Online SLAM with `slam_toolbox` in the `walls.sdf` world:

```bash
ros2 launch cybertruck slam.launch.py
```

Localization and navigation on the saved map (`config/my_map.yaml`):

```bash
ros2 launch cybertruck nav2.launch.py
```

`nav2.launch.py` starts `nav2_bringup` with AMCL (`slam:=False`), loads
`config/nav2_params.yaml`, and launches `cmd_vel_relay` automatically. Set an
initial pose in RViz with **2D Pose Estimate**, then send goals with
**Nav2 Goal**.

Common launch arguments:

| Argument    | Default        | Effect                                                              |
| ----------- | -------------- | ------------------------------------------------------------------- |
| `gz_args` | `-r <world>` | Gazebo arguments; append `-s` for headless                        |
| `drive`   | `true`       | Start the automatic circle-driving publisher (`gazebo.launch.py`) |
| `rviz`    | `true`       | Open RViz (`slam.launch.py`, `nav2.launch.py`)                  |

Worlds:

- `cybertruck.sdf` - open ground plane for free driving
- `walls.sdf` - enclosed room with pillars, used for SLAM and Nav2

---

### 5. Publisher / subscriber examples

C++:

```bash
ros2 run cpp_pubsub talker
ros2 run cpp_pubsub listener
# or both:
ros2 launch cpp_pubsub pubsub.launch.py
```

Python:

```bash
ros2 run py_pubsub talker
ros2 run py_pubsub listener
# or both:
ros2 launch py_pubsub pubsub.launch.py
```

A launch-composition demo that includes `pubsub.launch.py` and measures the
rate with `ros2 topic hz`:

```bash
ros2 launch py_pubsub demo.launch.py
```

Minimal scaffold node:

```bash
ros2 run my_package my_node
```

---

## Topics and frames

### testbot

| Topic                                             | Type                                           | Notes                                 |
| ------------------------------------------------- | ---------------------------------------------- | ------------------------------------- |
| `/clock`                                        | `rosgraph_msgs/msg/Clock`                    | bridged from Gazebo                   |
| `/joint_states`                                 | `sensor_msgs/msg/JointState`                 | from `joint_state_broadcaster`      |
| `/joint_trajectory_controller/joint_trajectory` | `trajectory_msgs/msg/JointTrajectory`        | elbow commands                        |
| `/camera/image_raw`, `/camera/camera_info`    | `sensor_msgs/msg/Image`, `CameraInfo`      | color camera                          |
| `/depth_camera/image_raw`                       | `sensor_msgs/msg/Image`                      | RGB                                   |
| `/depth_camera/depth/image_raw`                 | `sensor_msgs/msg/Image`                      | 32-bit depth                          |
| `/depth_camera/points_raw`                      | `sensor_msgs/msg/PointCloud2`                | retagged by `depth_cloud_frame_fix` |
| `/scan`, `/scan/points`                       | `sensor_msgs/msg/LaserScan`, `PointCloud2` | lidar                                 |

Kinematic chain:
`world -> head -> body -> shoulder -> upper_arm -> lower_arm -> hand`

### cybertruck

| Topic                  | Type                               | Notes                                                |
| ---------------------- | ---------------------------------- | ---------------------------------------------------- |
| `/scan`              | `sensor_msgs/msg/LaserScan`      | bridged as `/scan_raw`, retagged to `lidar_link` |
| `/diff_cont/cmd_vel` | `geometry_msgs/msg/TwistStamped` | diff-drive input                                     |
| `/cmd_vel`           | `geometry_msgs/msg/Twist`        | teleop / Nav2 output                                 |
| `/diff_cont/odom`    | `nav_msgs/msg/Odometry`          | wheel odometry                                       |

Frames: `map -> odom -> body -> wheels / lidar_link`

The controllers use `base_frame_id: body` and `odom_frame_id: odom`;
`wheel_separation` is 1.46 m and `wheel_radius` is 0.4175 m.
