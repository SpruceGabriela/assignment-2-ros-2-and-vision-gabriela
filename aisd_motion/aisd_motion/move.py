import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist

class Move(Node):
    def __init__(self):
        """
            Initializes the Move class, a node that subscribes to cmd_hand topic and converts the messages to Twist velocity commands."""
        super().__init__('move') # move is the name that appears on ROS2 list
        self.subscription = self.create_subscription(
            Hand, # the type of message of the subscription
            'cmd_hand', #your topic name published by hands in hands.py
            self.listener_callback,
            10) # the callback function that will be called when a new message is received, max queue is 10 (max number of messages buffered)
        self.subscription  # prevent unused variable warning
        self.vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10) #creates publisher that will publish the topic (channel between nodes) cmd_vel with max queue size of 10

    def listener_callback(self, msg):
        """
            listener_callback is called when a new message is received from the topic cmd_hand.
            It converts the message to Twist velocity commands and publishes it to the topic cmd_vel.
        """
        angle = 0.0 #angular velocity of the robot (how fast it turns)
        linear = 0.0 #linear velocity of the robot (how fast it moves forwards or backwards)
        if msg.xindex > 0.55: #closer to 1 means it's inclined to the right
            self.get_logger().info('right') # log message to show that the robot is turning right
            angle = -0.1 # turn to the right
        elif msg.xindex < 0.45: #closer to 0 means it's inclined to the left
            self.get_logger().info('left') # log message to show that the robot is turning left
            angle = 0.1 # turn to the left
        else:
            angle = 0.0 # set angle to 0 if the index finger is in the middle
        
        #if the index finger is to the right of the pinky finger, 
        # the hand is turned back to the camera (robot moves forward at 0.5), otherwise (palm facing the camera), it should stay still
        if msg.xindex > msg.xpinky:
            self.get_logger().info('come')
            linear = 0.5
        else:
            self.get_logger().info('stay')
            linear = 0.0

        #create a Twist message and set the linear and angular velocities
        twist = Twist()
        twist.linear.x = linear #it's x because the robot is moving forwards or backwards
        twist.angular.z = angle #rotation around the vertical z axis (left/right turn)
        
        #if vel_publisher has more than 0 subscribers, publish the twist message, otherwise, show a log message saying it's waiting for a subscriber
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)
        else:
            self.get_logger().info('waiting for subscriber')

def main(args=None):
    """
        main is the entry point called by ros2 defined in setup.py, it initializes Move 
        and keeps it running until the process ends.
    """
    rclpy.init(args=args)

    move = Move() #initialize Move class

    rclpy.spin(move) #keeps it running until the process is killed

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    move.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main() #run the main function if the file is called directly