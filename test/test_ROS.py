#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
import time

def move():
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=50)
    rospy.init_node("python_program", anonymous=True)

    ##
    #   Creation of the Twist, the object which will publish in the cmd_vel topic
    ##
    rate = rospy.Rate(10) # 10hz
    tps = time.time()
    cmd_vel = Twist()
    cmd_vel.linear.x = 0.0  # In front, value between -1 and 1
    cmd_vel.linear.y = 0.0  # On the side, value between -1 and 1
    cmd_vel.linear.z = 0.0  # Useless for Pepper
    cmd_vel.angular.x = 0.0 # Useless for Pepper
    cmd_vel.angular.y = 0.0 # Useless for Pepper
    cmd_vel.angular.z = 0.1 # Turn on itself, value between -1 and 1
        

    while time.time() - tps < 10 :
        pub.publish(cmd_vel) # Send the command on the cmd_vel topic
        rate.sleep()
    cmd_vel = Twist()
    cmd_vel.angular.z = 0.0 # Turn on itself, value between -1 and 1
    pub.publish(cmd_vel)    # Send the command on the cmd_vel topic

if __name__ == '__main__':
    try:
        move()
    except rospy.ROSInterruptException:
        pass
