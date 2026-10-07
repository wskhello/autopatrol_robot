import rclpy
from rclpy.node import Node
from autopatrol_interfaces.srv import SpeechText
import espeakng

class Speaker(Node):
    def __init__(self):
        super().__init__('speaker_node')
        self.speech_service_ = self.create_service(SpeechText,'/speech_text',self.speech_text_callback)
        self.speaker_ = espeakng.Speaker()
        self.speaker_.voice = 'zh' #设置中文语音

    def speech_text_callback(self,request,response):
        self.get_logger().info(f"正在准备朗读:{request.text}")
        self.speaker_.say(request.text) #朗读文本
        self.speaker_.wait() #等待朗读完成
        response.result = True
        return response

def main():
    rclpy.init()
    speaker_node = Speaker()
    rclpy.spin(speaker_node)
    rclpy.shutdown()