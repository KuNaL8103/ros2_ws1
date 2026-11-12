#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"

// Gazebo's rgbd_camera publishes the point cloud in the sensor frame
// (x forward, y left, z up) but stamps it with the optical frame id.
// The image really is optical, so only the cloud header is wrong.
//
// This relay copies the cloud unchanged and sets frame_id to the link
// frame, which is exactly the sensor frame. TF then rotates it into the
// optical frame / world correctly.
class DepthCloudFrameFix : public rclcpp::Node
{
public:
  DepthCloudFrameFix()
  : Node("depth_cloud_frame_fix")
  {
    auto qos = rclcpp::QoS(rclcpp::KeepLast(10));

    publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(
      "/depth_camera/points", qos);

    subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      "/depth_camera/points_raw", qos,
      [this](sensor_msgs::msg::PointCloud2::SharedPtr msg) {
        msg->header.frame_id = "depth_camera_link";
        publisher_->publish(*msg);
      });
  }

private:
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DepthCloudFrameFix>());
  rclcpp::shutdown();
  return 0;
}
