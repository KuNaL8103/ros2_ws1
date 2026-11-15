#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

// Gazebo stamps the scan with a scoped sensor frame
// (cybertruck/.../lidar_sensor). SLAM Toolbox expects the scan frame to
// exist in the URDF TF tree, so retag it as lidar_link.
class ScanFrameFix : public rclcpp::Node
{
public:
  ScanFrameFix()
  : Node("scan_frame_fix")
  {
    auto qos = rclcpp::QoS(rclcpp::KeepLast(10));

    publisher_ = this->create_publisher<sensor_msgs::msg::LaserScan>(
      "/scan", qos);

    subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      "/scan_raw", qos,
      [this](sensor_msgs::msg::LaserScan::SharedPtr msg) {
        msg->header.frame_id = "lidar_link";
        publisher_->publish(*msg);
      });
  }

private:
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr publisher_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ScanFrameFix>());
  rclcpp::shutdown();
  return 0;
}
