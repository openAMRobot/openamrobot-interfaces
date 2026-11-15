cmake_minimum_required(VERSION 3.8)
project(openamrobot_manipulation_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(action_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  # Actions
  "action/ExecutePlan.action"
  "action/MoveToNamedPose.action"
  "action/GripperCommand.action"
  "action/CartesianMotion.action"
  "action/MoveUntilContact.action"
  "action/CompliantHold.action"
  "action/AbortTask.action"

  # Services
  "srv/Plan.srv"
  "srv/QueryCapabilities.srv"
  "srv/GetPlanPreview.srv"
  "srv/Stop.srv"
  "srv/RequestOwnership.srv"
  "srv/RenewOwnership.srv"
  "srv/ReleaseOwnership.srv"

  # Messages
  "msg/PlacementGoal.msg"
  "msg/ActionResult.msg"
  "msg/CommandContext.msg"
  "msg/WorkspaceEnvelope.msg"
  "msg/ComplianceParameters.msg"
  "msg/OwnershipState.msg"
  "msg/PlanningConstraints.msg"
  "msg/ManipulatorSelector.msg"

  DEPENDENCIES
    action_msgs
    builtin_interfaces
    geometry_msgs
    sensor_msgs
    trajectory_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
