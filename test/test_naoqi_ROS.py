import time
import rospy
from geometry_msgs.msg import Twist
from naoqi import ALProxy

class MoveAndTalk:

    def __init__(self, node_name, robot_adress, robot_port):
        """
        Constructor of the MoveAndTalk Class

        :param node_name: name of the ros node
        :param robot_adress: Ip adress of the robot
        :param robot_port: Port use to connect to the robot

        """
        self.ros = {}
        self.naoqi = {}
        self.ros["node_name"] = node_name
        self.naoqi["tts"] = ALProxy("ALTextToSpeech", robot_adress, robot_port) ## Initialize the Text to speech module
        rospy.init_node(self.ros["node_name"], anonymous=True)

    def start(self):
        """
        Method which call all other method
        """
        self.moveRobot(0.1)
        self.talk("Je me deplace, youpii !!!")
        time.sleep(3)
        self.stopRobot()


    def moveRobot(self, speed):
        """
        Methode to do move the robot

        :param speed: speed of the robot's move
        """
        self.ros["pub"] = rospy.Publisher('cmd_vel', Twist, queue_size=50)

        ##
        #   Creation of the Twist, the object which will publish in the cmd_vel topic
        ##
        rate = rospy.Rate(10) # 10hz
        tps = time.time();
        while time.time() - tps < 0.5 :
            self.ros["cmd_vel"] = Twist()
            self.ros["cmd_vel"].linear.x = speed  # In front
            self.ros["cmd_vel"].linear.y = 0.0  # On the side
            self.ros["cmd_vel"].linear.z = 0.0  # Useless for Pepper
            self.ros["cmd_vel"].angular.x = 0.0 # Useless for Pepper
            self.ros["cmd_vel"].angular.y = 0.0 # Useless for Pepper
            self.ros["cmd_vel"].angular.z = 0.0 # Turn on itself
            self.ros["pub"].publish(self.ros["cmd_vel"])    # Send the command on the cmd_vel topic
            rate.sleep()

    def stopRobot(self):
        """
        Method to stop the movement of the robot
        """
        pub = rospy.Publisher('cmd_vel', Twist, queue_size=50)

        ##
        #   Creation of the Twist, the object which will publish in the cmd_vel topic
        ##
        rate = rospy.Rate(10) # 10hz
        tps = time.time();
        while time.time() - tps < 0.5 :
            cmd_vel = Twist()
            cmd_vel.linear.x = 0.0  # In front, value between -1 and 1
            cmd_vel.linear.y = 0.0  # On the side, value between -1 and 1
            cmd_vel.linear.z = 0.0  # Useless for Pepper
            cmd_vel.angular.x = 0.0 # Useless for Pepper
            cmd_vel.angular.y = 0.0 # Useless for Pepper
            cmd_vel.angular.z = 0.0 # Turn on itself, value between -1 and 1
            pub.publish(cmd_vel)    # Send the command on the cmd_vel topic
            rate.sleep()

    def talk(self, text):
        """
        Method to do talking the robot

        :param text: text says by the robot"""
        self.naoqi["tts"].say("%s" %text)   ## Send the text to the robot

if __name__ == '__main__':
    try:
        ##
        #   IP address of the robot
        ##
        adresse = "100.75.166.171"

        ##
        #   Port used by the robot, it could change in simulation
        ##
        port = 9559
        mat = MoveAndTalk("PythonProgramm", adresse, port)
        mat.start()
    except rospy.ROSInterruptException:
        pass
