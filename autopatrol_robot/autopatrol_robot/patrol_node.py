import rclpy
from geometry_msgs.msg import PoseStamped,Pose
from nav2_simple_commander.robot_navigator import BasicNavigator,TaskResult
import rclpy.time
from tf_transformations import euler_from_quaternion, quaternion_from_euler #四元数转欧拉角
from tf2_ros import TransformListener, Buffer #坐标变换监听器和缓存
from autopatrol_interfaces.srv import SpeechText
from std_srvs.srv import Trigger


class PatrolNode(BasicNavigator):
    def __init__(self,node_name='patrol_robot'):
        super().__init__(node_name)

        #声明相关参数
        self.declare_parameter('initial_point',[0.0,0.0,0.0]) #初始点
        self.declare_parameter('target_points',[0.0,0.0,0.0,1.0,1.0,1.57]) #目标点列表,每三个数字作为一个点的x,y,theta
        self.initial_point_ = self.get_parameter('initial_point').value
        self.target_points_ = self.get_parameter('target_points').value
        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_,self)
        self.speech_client_ = self.create_client(SpeechText,'speech_text') #创建语音服务客户端
        self.image_client_ = self.create_client(Trigger,'take_photo')

    def get_pose_by_xyyaw(self,x,y,yaw):
        """
        根据x,y,yaw获取PoseStamped对象
        """
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        quta = quaternion_from_euler(0,0,yaw) #将欧拉角转换为四元数
        pose.pose.orientation.x = quta[0]
        pose.pose.orientation.y = quta[1]
        pose.pose.orientation.z = quta[2]   
        pose.pose.orientation.w = quta[3]
        return pose
    
    def init_robot_pose(self):
        """
        初始化机器人位姿
        """
        init_pose = self.get_pose_by_xyyaw(self.initial_point_[0],self.initial_point_[1],self.initial_point_[2])
        self.setInitialPose(init_pose)
        self.waitUntilNav2Active() #等待导航系统激活

    def get_target_points(self):
        """
        通过参数值获取目标点集合
        """
        points = []
        for i in range(0,len(self.target_points_),3):
            x = self.target_points_[i]
            y = self.target_points_[i+1]
            yaw = self.target_points_[i+2]
            points.append([x, y, yaw])
            self.get_logger().info(f"获取到目标点:{x},{y},{yaw}")
        return points

    def nav_to_pose(self,target_point):
        """
        导航到目标点
        """
        self.goToPose(target_point) #发送导航目标点
        while not self.isTaskComplete(): #等待导航完成
            feedback = self.getFeedback() #获取导航反馈信息
            if feedback:
                self.get_logger().info(f"剩余距离:{feedback.distance_remaining}") #打印导航反馈信息
        result = self.getResult() #获取导航结果
        self.get_logger().info(f"导航结果:{result}") #打印导航结果
        return result

    def get_current_pose(self):
        """
        获取当前位姿
        """
        while rclpy.ok():
            try:
                result = self.buffer_.lookup_transform('map','base_footprint',rclpy.time.Time(seconds=0),rclpy.time.Duration(seconds=1.0))
                transform = result.transform #获取变换信息
                self.get_logger().info(f"平移:{transform.translation}...")
                self.get_logger().info(f"旋转:{transform.rotation}...")
                rotation_euler = euler_from_quaternion([ #将四元数转换为欧拉角
                    transform.rotation.x,
                    transform.rotation.y,
                    transform.rotation.z,
                    transform.rotation.w,   
                ])
                self.get_logger().info(f"旋转(RPY):{rotation_euler}...")
            except Exception as e:
                self.get_logger().info(f"异常:{e}...")

    # def speech_text(self,text):
    #     """
    #     调用服务合成语音
    #     """
    #     while not self.speech_client_.wait_for_service(timeout_sec=1.0):
    #         self.get_logger().info('服务不可用，等待中...')
    #     request = SpeechText.Request()
    #     request.text = text
    #     future = self.speech_client_.call_async(request)
    #     rclpy.spin_until_future_complete(self,future)
    #     if future.result() is not None:
    #         self.get_logger().info(f"语音合成结果:{future.result().result}")

    def speech_text(self, text, timeout_sec=3.0, wait_sec=1.0):
        """调用服务合成语音。服务不可用时不阻塞、不抛异常,只告警。"""

        if not self.speech_client_.wait_for_service(timeout_sec=wait_sec):
            self.get_logger().warn(f'语音服务不可用,跳过播报: {text}')
            return False

        request = SpeechText.Request()
        request.text = text
        future = self.speech_client_.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout_sec)

        if not future.done():
            self.get_logger().warn(f'语音服务无响应,跳过: {text}')
            return False
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().warn(f'语音调用异常,跳过: {e}')
            return False

        self.get_logger().info(f'语音合成结果: {response.result}')
        return True

    def save_photo(self):

        while not self.image_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('服务不可用，等待中...')

        future = self.image_client_.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future)
        if not future.done():
            self.get_logger().warn('拍照服务无响应(超时)')
            return False

        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error(f'拍照调用异常: {e}')
            return False

        if response is None:
            self.get_logger().error('拍照服务返回空')
            return False

        self.get_logger().info(
            f'保存图片: success={response.success} msg={response.message}')
        return response.success

   

def main():
    rclpy.init()
    patrol_node = PatrolNode()
    patrol_node.speech_text('正在准备初始化位置')
    patrol_node.init_robot_pose() #初始化机器人位姿
    patrol_node.speech_text('初始化位置完成')
    while rclpy.ok():
        points = patrol_node.get_target_points() #获取目标点集合
        for point in points:
            x,y,yaw = point[0],point[1],point[2]
            target_pose = patrol_node.get_pose_by_xyyaw(x,y,yaw) #获取目标点的PoseStamped对象
            patrol_node.speech_text(f'正在准备前往{x},{y}点')
            result = patrol_node.nav_to_pose(target_pose) #导航到目标点
            if result == TaskResult.SUCCEEDED:
                patrol_node.save_photo()
        rclpy.spin_once(patrol_node, timeout_sec=0.5)        


    rclpy.shutdown()
   