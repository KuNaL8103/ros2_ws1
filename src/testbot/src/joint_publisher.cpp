#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"

using namespace std::chrono_literals;

class JointPublisher : public rclcpp::Node
{
public:
  JointPublisher()
  : Node("joint_publisher"), sign_(1.0)
  {
    // topic is /<controller_name>/joint_trajectory - the name matters
    publisher_ = this->create_publisher<trajectory_msgs::msg::JointTrajectory>(
      "/joint_trajectory_controller/joint_trajectory", 10);

    timer_ = this->create_wall_timer(
      2s, std::bind(&JointPublisher::send_trajectory, this));
  }

private:
  void send_trajectory()
  {
    trajectory_msgs::msg::JointTrajectory msg;
    msg.joint_names = {
      "upper_arm_to_lower_arm_right",
      "upper_arm_to_lower_arm_left"};

    trajectory_msgs::msg::JointTrajectoryPoint point;
    point.positions = {0.5 * sign_, 0.5 * sign_};
    point.time_from_start.sec = 2;
    point.time_from_start.nanosec = 0;
    msg.points.push_back(point);

    RCLCPP_INFO(
      this->get_logger(), "Sending elbows to [%.2f, %.2f] over 2 s",
      point.positions[0], point.positions[1]);
    publisher_->publish(msg);

    sign_ = -sign_;
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr publisher_;
  double sign_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<JointPublisher>());
  rclcpp::shutdown();
  return 0;
}
