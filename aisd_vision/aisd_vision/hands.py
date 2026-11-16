import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp
mp_hands = mp.solutions.hands

from aisd_msgs.msg import Hand

class Hands(Node):

    def __init__(self):
        """
            Initializes the Hands class, a node that subscribes to image_publisher node
            It processes the images to detect hands and publishes the position of the index finger and pinky finger to the topic cmd_hand.
        """
        super().__init__('hands') # hands is the name that appears on ROS2 list
        self.subscription = self.create_subscription(
            Image, # the type of message of the subscription
            'video_frames', #your topic name published by image_publisher in image_publisher.py
            self.listener_callback,
            10) # the callback function that will be called when a new message is received, max queue is 10 (maximum number of messages buffered)
        self.subscription  # prevent unused variable warning

        # A converter between ROS2 and OpenCV images
        self.br = CvBridge() #instantiates a CvBridge object to convert ROS2 images to OpenCV images and vice versa
        self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10) #creates publisher that will publish the topic (channel between nodes) cmd_hand with max queue size of 10


    def listener_callback(self, msg):
        """
            listener_callback is called when a new image is received from the topic video_frames.
            It processes the image to detect hands and publishes the position of the index finger and pinky finger to the topic cmd_hand.
        """
        image = self.br.imgmsg_to_cv2(msg) # converts the msg (ROS2 image) into OpenCV image (numpy matrix of pixels)

        PINKY_FINGER_TIP = 20 #landmark index of the tip of the pinky finger from 0 to 20
        INDEX_FINGER_TIP = 8 #landmark index of the tip of the index finger from 0 to 20

        # Analyse the image for hands using MediaPipe Hands, a machine learning model that detect hands and their landmarks
        with mp_hands.Hands( 
            model_complexity=0, #fastest model
            min_detection_confidence=0.5, #minimum confidence value
            min_tracking_confidence=0.5) as myhands:

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #cv2 converts color to RGB, MediaPipe's format
            results = myhands.process(image) #results of processed image
            if results.multi_hand_landmarks:
                #publish the hand position in terms of index finger and pinky
                msg = Hand() #create a new Hand empty message (defined in aisd_msgs) that will be filled in the next steps, then published on cmd_hand

                #x axis is normalized from 0.0 (left) to 1.0 (right)
                msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x #gets pinky finger position in x axis
                msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x #gets index finger position in x axis

                #if there are more than 0 subscribers, publish message, otherwise, shows a log saying it's waiting
                if self.hand_publisher.get_subscription_count() > 0:
                    self.hand_publisher.publish(msg)
                else:
                    self.get_logger().info('waiting for subcriber')

def main(args=None):
    """
        main is the entry point called by ros2 defined in setup.py, it initializes Hands 
        and keeps it running until the process ends.
    """
    rclpy.init(args=args)

    hands = Hands() #initialize Hands class

    rclpy.spin(hands) #keeps it running until the process is killed

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    hands.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main() #run the main function if the file is called directly