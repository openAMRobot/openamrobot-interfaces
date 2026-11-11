cmake_minimum_required(VERSION 3.8)
project(openamr_base_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(builtin_interfaces REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BaseStatus.msg"
  "msg/BaseAuxStatus.msg"
  "msg/BaseFault.msg"
  "msg/BaseSubsystemStatus.msg"
  "msg/BaseMotionConstraint.msg"
  DEPENDENCIES
    builtin_interfaces
    std_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
