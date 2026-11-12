#include <iostream>

#include "openamr_nav_msgs/msg/navigation_status.hpp"
#include "openamr_ui_msgs/action/move_base.hpp"
#include "openamr_ui_msgs/msg/array_pose_stamped_with_covariance.hpp"

#include "openamrobot_manipulation_interfaces/msg/action_result.hpp"
#include "openamrobot_manipulation_interfaces/msg/command_context.hpp"
#include "openamrobot_manipulation_interfaces/msg/compliance_parameters.hpp"
#include "openamrobot_manipulation_interfaces/msg/manipulator_selector.hpp"
#include "openamrobot_manipulation_interfaces/msg/ownership_state.hpp"
#include "openamrobot_manipulation_interfaces/msg/placement_goal.hpp"
#include "openamrobot_manipulation_interfaces/msg/planning_constraints.hpp"
#include "openamrobot_manipulation_interfaces/msg/workspace_envelope.hpp"

#include "openamrobot_manipulation_interfaces/srv/get_plan_preview.hpp"
#include "openamrobot_manipulation_interfaces/srv/plan.hpp"
#include "openamrobot_manipulation_interfaces/srv/query_capabilities.hpp"
#include "openamrobot_manipulation_interfaces/srv/release_ownership.hpp"
#include "openamrobot_manipulation_interfaces/srv/renew_ownership.hpp"
#include "openamrobot_manipulation_interfaces/srv/request_ownership.hpp"
#include "openamrobot_manipulation_interfaces/srv/stop.hpp"

#include "openamrobot_manipulation_interfaces/action/abort_task.hpp"
#include "openamrobot_manipulation_interfaces/action/cartesian_motion.hpp"
#include "openamrobot_manipulation_interfaces/action/compliant_hold.hpp"
#include "openamrobot_manipulation_interfaces/action/execute_plan.hpp"
#include "openamrobot_manipulation_interfaces/action/gripper_command.hpp"
#include "openamrobot_manipulation_interfaces/action/move_to_named_pose.hpp"
#include "openamrobot_manipulation_interfaces/action/move_until_contact.hpp"

#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
#include "rosidl_typesupport_cpp/action_type_support.hpp"

int main()
{
  // Existing navigation and UI interfaces.
  using NavigationStatus = openamr_nav_msgs::msg::NavigationStatus;
  using Poses = openamr_ui_msgs::msg::ArrayPoseStampedWithCovariance;
  using MoveBase = openamr_ui_msgs::action::MoveBase;

  NavigationStatus status;
  status.contract_version = NavigationStatus::CONTRACT_VERSION;

  Poses poses;
  poses.poses.resize(1);

  MoveBase::Goal move_base_goal;
  move_base_goal.target.header.frame_id = "map";

  // Manipulation messages.
  using ActionResult =
    openamrobot_manipulation_interfaces::msg::ActionResult;
  using CommandContext =
    openamrobot_manipulation_interfaces::msg::CommandContext;
  using ComplianceParameters =
    openamrobot_manipulation_interfaces::msg::ComplianceParameters;
  using ManipulatorSelector =
    openamrobot_manipulation_interfaces::msg::ManipulatorSelector;
  using OwnershipState =
    openamrobot_manipulation_interfaces::msg::OwnershipState;
  using PlacementGoal =
    openamrobot_manipulation_interfaces::msg::PlacementGoal;
  using PlanningConstraints =
    openamrobot_manipulation_interfaces::msg::PlanningConstraints;
  using WorkspaceEnvelope =
    openamrobot_manipulation_interfaces::msg::WorkspaceEnvelope;

  ActionResult action_result;
  CommandContext command_context;
  ComplianceParameters compliance_parameters;
  ManipulatorSelector manipulator_selector;
  OwnershipState ownership_state;
  PlacementGoal placement_goal;
  PlanningConstraints planning_constraints;
  WorkspaceEnvelope workspace_envelope;

  // Manipulation services.
  using GetPlanPreview =
    openamrobot_manipulation_interfaces::srv::GetPlanPreview;
  using Plan =
    openamrobot_manipulation_interfaces::srv::Plan;
  using QueryCapabilities =
    openamrobot_manipulation_interfaces::srv::QueryCapabilities;
  using ReleaseOwnership =
    openamrobot_manipulation_interfaces::srv::ReleaseOwnership;
  using RenewOwnership =
    openamrobot_manipulation_interfaces::srv::RenewOwnership;
  using RequestOwnership =
    openamrobot_manipulation_interfaces::srv::RequestOwnership;
  using Stop =
    openamrobot_manipulation_interfaces::srv::Stop;

  GetPlanPreview::Request preview_request;
  GetPlanPreview::Response preview_response;
  Plan::Request plan_request;
  Plan::Response plan_response;
  QueryCapabilities::Request capabilities_request;
  QueryCapabilities::Response capabilities_response;
  ReleaseOwnership::Request release_request;
  ReleaseOwnership::Response release_response;
  RenewOwnership::Request renew_request;
  RenewOwnership::Response renew_response;
  RequestOwnership::Request ownership_request;
  RequestOwnership::Response ownership_response;
  Stop::Request stop_request;
  Stop::Response stop_response;

  // Manipulation actions.
  using AbortTask =
    openamrobot_manipulation_interfaces::action::AbortTask;
  using CartesianMotion =
    openamrobot_manipulation_interfaces::action::CartesianMotion;
  using CompliantHold =
    openamrobot_manipulation_interfaces::action::CompliantHold;
  using ExecutePlan =
    openamrobot_manipulation_interfaces::action::ExecutePlan;
  using GripperCommand =
    openamrobot_manipulation_interfaces::action::GripperCommand;
  using MoveToNamedPose =
    openamrobot_manipulation_interfaces::action::MoveToNamedPose;
  using MoveUntilContact =
    openamrobot_manipulation_interfaces::action::MoveUntilContact;

  AbortTask::Goal abort_goal;
  AbortTask::Result abort_result;
  AbortTask::Feedback abort_feedback;

  CartesianMotion::Goal cartesian_goal;
  CartesianMotion::Result cartesian_result;
  CartesianMotion::Feedback cartesian_feedback;

  CompliantHold::Goal compliant_goal;
  CompliantHold::Result compliant_result;
  CompliantHold::Feedback compliant_feedback;

  ExecutePlan::Goal execute_goal;
  ExecutePlan::Result execute_result;
  ExecutePlan::Feedback execute_feedback;

  GripperCommand::Goal gripper_goal;
  GripperCommand::Result gripper_result;
  GripperCommand::Feedback gripper_feedback;

  MoveToNamedPose::Goal named_pose_goal;
  MoveToNamedPose::Result named_pose_result;
  MoveToNamedPose::Feedback named_pose_feedback;

  MoveUntilContact::Goal contact_goal;
  MoveUntilContact::Result contact_result;
  MoveUntilContact::Feedback contact_feedback;

  // Verify message type support.
  const bool messages_ok =
    rosidl_typesupport_cpp::get_message_type_support_handle<NavigationStatus>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<Poses>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<MoveBase::Goal>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<ActionResult>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<CommandContext>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<ComplianceParameters>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<ManipulatorSelector>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<OwnershipState>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<PlacementGoal>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<PlanningConstraints>() &&
    rosidl_typesupport_cpp::get_message_type_support_handle<WorkspaceEnvelope>();

  // Verify service type support.
  const bool services_ok =
    rosidl_typesupport_cpp::get_service_type_support_handle<GetPlanPreview>() &&
    rosidl_typesupport_cpp::get_service_type_support_handle<Plan>() &&
    rosidl_typesupport_cpp::get_service_type_support_handle<QueryCapabilities>() &&
    rosidl_typesupport_cpp::get_service_type_support_handle<ReleaseOwnership>() &&
    rosidl_typesupport_cpp::get_service_type_support_handle<RenewOwnership>() &&
    rosidl_typesupport_cpp::get_service_type_support_handle<RequestOwnership>() &&
    rosidl_typesupport_cpp::get_service_type_support_handle<Stop>();

  // Verify action type support.
  const bool actions_ok =
    rosidl_typesupport_cpp::get_action_type_support_handle<AbortTask>() &&
    rosidl_typesupport_cpp::get_action_type_support_handle<CartesianMotion>() &&
    rosidl_typesupport_cpp::get_action_type_support_handle<CompliantHold>() &&
    rosidl_typesupport_cpp::get_action_type_support_handle<ExecutePlan>() &&
    rosidl_typesupport_cpp::get_action_type_support_handle<GripperCommand>() &&
    rosidl_typesupport_cpp::get_action_type_support_handle<MoveToNamedPose>() &&
    rosidl_typesupport_cpp::get_action_type_support_handle<MoveUntilContact>();

  if (!messages_ok) {
    std::cerr << "FAIL: message type support unavailable\n";
    return 1;
  }

  if (!services_ok) {
    std::cerr << "FAIL: service type support unavailable\n";
    return 1;
  }

  if (!actions_ok) {
    std::cerr << "FAIL: action type support unavailable\n";
    return 1;
  }

  std::cout << "PASS: navigation and UI interfaces\n";
  std::cout << "PASS: 8 manipulation messages\n";
  std::cout << "PASS: 7 manipulation services\n";
  std::cout << "PASS: 7 manipulation actions\n";
  std::cout << "PASS: all installed C++ type-support handles\n";

  return 0;
}
