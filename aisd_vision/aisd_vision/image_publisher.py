import rclpy # rclpy is the client library for Python (acts as a bridge between ROS2 and Python)
from rclpy.node import Node
from sensor_msgs.msg import Image

from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2


class ImagePublisher(Node):
    def __init__(self):
        """
            Initializes the ImagePublisher class, this is a node (a worker doing an specific job).
            It was created to publish images from the webcam to the topic (an channel where nodes can exchange information) 
            called video_frames. It gets updated every 0.1 seconds.
            cv_bridge is a library that converts OpenCV (Computer Vision Library) images to ROS2 images and vice versa.
        """
        super().__init__("image_publisher")
        self.publisher_ = self.create_publisher(Image, "video_frames", 10) #create a publisher that will publish to the topic video_frames with a queue size of 10 (max messages buffered)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback) # create a timer that will call timer_callback every timer_period seconds
        self.cap = cv2.VideoCapture(0) # create a VideoCapture object to read from the webcam, 0 is the default camera
        self.br = CvBridge() # create a CVBridge object to convert webcam images to ROS2 images

    def timer_callback(self):
        """
            timer_callback reads the webcam and publishes the image to the topic 
            video_frames every 0.1 seconds since it's being called by the timer.
        """
        ret, frame = self.cap.read() #ret is a boolean indicating if the camera was able to capture an image, and frame is the image itself represented by a numpy matrix of pixels
        if ret == True:
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame)) # if ret is true, the self_publisher publish the image converted to ROS2 format using cv2


def main(args=None):
    """
       main is the entry point called by ros2 defined in setup.py, it initializes ImagePublisher 
        and keeps it running until the process ends.
    """
    rclpy.init(args=args)

    image_publisher = ImagePublisher() # ininitalize the ImagePublisher class

    rclpy.spin(image_publisher) # keeps the node running until it's killed

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    image_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main() # run the main function if this file is excuted directly
