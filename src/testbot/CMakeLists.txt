cmake_minimum_required(VERSION 3.8)
project(testbot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

add_executable(joint_publisher src/joint_publisher.cpp)
ament_target_dependencies(joint_publisher rclcpp trajectory_msgs)

add_executable(depth_cloud_frame_fix src/depth_cloud_frame_fix.cpp)
ament_target_dependencies(depth_cloud_frame_fix rclcpp sensor_msgs)

install(TARGETS
  joint_publisher
  depth_cloud_frame_fix
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  urdf
  config
  worlds
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
