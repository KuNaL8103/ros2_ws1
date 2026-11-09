cmake_minimum_required(VERSION 3.8)
project(my_robot)

find_package(ament_cmake REQUIRED)

# install assets so get_package_share_directory('my_robot') finds them at runtime
install(DIRECTORY
  urdf
  meshes
  config
  launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
