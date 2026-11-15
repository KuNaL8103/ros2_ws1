#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "rclcpp/rclcpp.hpp"

// Nav2 (and teleop_twist_keyboard) publish geometry_msgs/msg/Twist on
// /cmd_vel. Jazzy's diff_drive_controller wants TwistStamped on
// /diff_cont/cmd_vel, so convert and timestamp here.
class CmdVelRelay : public rclcpp::Node
{
public:
  CmdVelRelay()
  : Node("cmd_vel_relay")
  {
    publisher_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
      "/diff_cont/cmd_vel", 10);

    subscription_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel", 10,
      [this](geometry_msgs::msg::Twist::SharedPtr msg) {
        geometry_msgs::msg::TwistStamped out;
        out.header.stamp = this->get_clock()->now();
        out.header.frame_id = "body";
        out.twist = *msg;
        publisher_->publish(out);
      });
  }

private:
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdVelRelay>());
  rclcpp::shutdown();
  return 0;
}
