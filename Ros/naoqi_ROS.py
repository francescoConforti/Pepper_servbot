import time
import rospy
from geometry_msgs.msg import Twist
from naoqi import ALProxy
from math import pi
import math
from nav_msgs.msg import Odometry

#roscore
#roslaunch pepper_bringup pepper_full.launch nao_ip:=100.75.166.171 network_interface:=wlan0

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
        # Donnees de la rotation.
        self.angle = 0
        self.moveAngle = 0
        #self.naoqi["tts"] = ALProxy("ALTextToSpeech", robot_adress, robot_port) ## Initialize the Text to speech module
        rospy.Subscriber("pepper_robot/naoqi_driver/odom", Odometry, self.odometry) # /pepper_robot/naoqi_driver/odom
        rospy.init_node(self.ros["node_name"], anonymous=True)
         #GeneratedClass.__init__(self, False)
        
        self.motion = ALProxy("ALMotion", robot_adress, robot_port)
        self.positionErrorThresholdPos = 0.01
        self.positionErrorThresholdAng = 0.03

        
    def odometry(self, data):
        self.angle = data.pose.pose.orientation.z
        self.moveAngle = data.twist.twist.angular.z

        
    def start(self):
        """
        Method which call all other method
        """
        self.moveRobot(0.5,0,90)
        self.moveRobot(0.5,0,90)
        self.moveRobot(0.5,0,90)
        self.moveRobot(0.5,0,90)
        #self.stopRobot();
        
    def moveRobot(self, X, Y, Deg):
        import almath
        # The command position estimation will be set to the sensor position
        # when the robot starts moving, so we use sensors first and commands later.
        initPosition = almath.Pose2D(self.motion.getRobotPosition(True))
        targetDistance = almath.Pose2D(X, Y,Deg* almath.PI / 180)
        expectedEndPosition = initPosition * targetDistance
        #enableArms = self.getParameter("Arms movement enabled")
        #self.motion.setMoveArmsEnabled(enableArms, enableArms)
        self.motion.moveTo(X,Y,Deg * almath.PI / 180)

        # The move is finished so output
        realEndPosition = almath.Pose2D(self.motion.getRobotPosition(False))
        positionError = realEndPosition.diff(expectedEndPosition)
        positionError.theta = almath.modulo2PI(positionError.theta)
        if (abs(positionError.x) < self.positionErrorThresholdPos
            and abs(positionError.y) < self.positionErrorThresholdPos
            and abs(positionError.theta) < self.positionErrorThresholdAng):
            print("ARRIVER")
            #self.onArrivedAtDestination()
        else:
            print("ERREUR")
            #self.onStoppedBeforeArriving(positionError.toVector())
        
    def stopRobot(self):
        """
        #Method to stop the movement of the robot
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
        print("Debut ROBOT")
        mat.start()
        
        mat.stopRobot()
        print("FIN ROBOT")
    except rospy.ROSInterruptException:
        pass
