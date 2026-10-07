import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener #坐标变换监听器
from tf2_ros import Buffer
from rclpy.time import Time
from rclpy.duration import Duration  
from tf_transformations import euler_from_quaternion #四元数转欧拉角

class TFlistener(Node):
    def __init__(self,node_name):
        super().__init__(node_name)
        self.buffer_ = Buffer()#这是tf2_ros的缓存对象，存储了所有的坐标变换信息
        self.listener_= TransformListener(self.buffer_,self)#坐标变换监听器，监听tf2的坐标变换信息，并将其存储到缓存对象中
        self.timer = self.create_timer(1,self.get_transform)

    def get_transform(self):
        """
        实时查询坐标关系
        """
        try:
            result = self.buffer_.lookup_transform('map','base_footprint',Time(seconds=0),Duration(seconds=1.0))#这是tf2_ros的缓存对象的查询方法，查询A坐标系到B坐标系的变换关系
            transform = result.transform
            self.get_logger().info(f"平移:{transform.translation}...")
            self.get_logger().info(f"旋转:{transform.rotation}...")
            rotation_euler = euler_from_quaternion([
                transform.rotation.x,
                transform.rotation.y,
                transform.rotation.z,
                transform.rotation.w,   
            ])
            self.get_logger().info(f"旋转(RPY):{rotation_euler}...")
            
        except Exception as e:
            self.get_logger().info(f"异常:{e}...")

def main():
    rclpy.init()
    node = TFlistener('tf_li')
    rclpy.spin(node)
    rclpy.shutdown()