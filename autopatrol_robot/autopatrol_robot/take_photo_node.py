import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_srvs.srv import Trigger
#Trigger消息接口:
#   ---
#   bool success
#   string message  无需参数
import cv2

class TakePhotoNode(Node):
    def __init__(self,nodename):
        super().__init__(nodename)
        self.image_ = None
        self.bridge_ = CvBridge()
        self.subscripter_ = self.create_subscription(Image,'/camera_sensor/image_raw',self.image_callback,10)
        self.image_service_ = self.create_service(Trigger,'/take_photo',self.take_photo_cb)

    def image_callback(self,msg:Image):
        self.get_logger().info(
            f'{msg.width}x{msg.height} enc={msg.encoding} '
            f'bytes={len(msg.data)} frame={msg.header.frame_id}'
        )
        self.image_ = msg

    def take_photo_cb(self, request, response):
        if self.image_ is None:
            response.success = False
            response.message = '还没有收到图像帧'
            return response
        frame = self.bridge_.imgmsg_to_cv2(self.image_, desired_encoding='bgr8')
        cv2.imwrite('camera.jpg', frame)
        response.success = True 
        response.message = 'saved camera.jpg'
        return response

def main():
    rclpy.init()
    take_photo = TakePhotoNode('take_photo_node')
    rclpy.spin(take_photo)
    rclpy.shutdown()

    


        