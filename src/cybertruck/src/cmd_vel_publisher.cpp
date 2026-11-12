#include <chrono>
#include <memory>

#include "geometry_msgs/msg/twist_stamped.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

// Drive in a 1 m radius circle: v = 0.1 m/s, omega = 0.1 rad/s.
//
// Jazzy's diff_drive_controller subscribes to ~/cmd_vel with
// geometry_msgs/msg/TwistStamped (the Humble-era use_stamped_vel=false
// option is gone). A plain Twist is silently ignored.
class CmdVelPublisher : public rclcpp::Node
{
public:
  CmdVelPublisher()
  : Node("cmd_vel_publisher")
  {
    publisher_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
      "/diff_cont/cmd_vel", 10);

    timer_ = this->create_wall_timer(
      100ms, std::bind(&CmdVelPublisher::publish_cmd, this));

    RCLCPP_INFO(
      this->get_logger(),
      "Publishing TwistStamped v=0.1 m/s, omega=0.1 rad/s "
      "on /diff_cont/cmd_vel");
  }

private:
  void publish_cmd()
  {
    geometry_msgs::msg::TwistStamped msg;
    msg.header.stamp = this->get_clock()->now();
    msg.header.frame_id = "body";
    msg.twist.linear.x = 0.1;
    msg.twist.angular.z = 0.1;
    publisher_->publish(msg);
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdVelPublisher>());
  rclcpp::shutdown();
  return 0;
}
