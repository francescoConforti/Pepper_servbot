#!/usr/bin/python

from sys import stdout
import scipy.ndimage.morphology as dilateur
import numpy as np
import heapq as heap
import math
import copy
import time
import rospy
import almath
from geometry_msgs.msg import Twist
from naoqi import ALProxy
from math import pi
from nav_msgs.msg import Odometry


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

        self.initPosition = almath.Pose2D(self.motion.getRobotPosition(True))
        self.position = self.initPosition
        
    def odometry(self, data):
        self.angle = data.pose.pose.orientation.z
        self.moveAngle = data.twist.twist.angular.z

        
    def start(self):
        """
        Method which call all other method
        """
        #self.stopRobot();
        
    def moveRobot(self, X, Y, Deg):
        # The command position estimation will be set to the sensor position
        # when the robot starts moving, so we use sensors first and commands later.
        startPosition = almath.Pose2D(self.motion.getRobotPosition(True))
        targetDistance = almath.Pose2D(X, Y,Deg* almath.PI / 180)
        expectedEndPosition = startPosition * targetDistance
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
        #print(self.initPosition,startPosition,realEndPosition)
        self.position = realEndPosition
        
    """def stopRobot(self):
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
            rate.sleep()"""

    def talk(self, text):
        """
        Method to do talking the robot

        :param text: text says by the robot"""
        self.naoqi["tts"].say("%s" %text)   ## Send the text to the robot


rayonPepper = 3 # Dimention 42.5 48.5

# Methode qui recupere la map namefile et la charge dans le tableau map
# param filename : string : nom du fichier contenant la carte  
# retrn : list : carte chargee 
def loadMap(filename):
    # Ouverture du fichier 
    print("Ouverture du fichier " + filename)
    f = open(filename, "r")
    # Lecture du fichier
    s = f.read()
    s = s.split("\n")
    # Recuperation des dimentions de la carte 
    width = int(s[2].split()[0])
    height = int(s[2].split()[1])
    # Initialisation du tableau map 
    map = [[0 for i in range(width)] for j in range(height)]
    # Recuperation des donnees 
    print("Chargement des donnees ")
    for j in range(height):
        line = s[4 + j].split()
        for i in range(width):
            map[j][i] = int(line[i])
    print("Chargement termine")
    # Fermeture du fichier
    f.close()
    return map

# Methode qui permet de sauvegarder la carte passe en parametre
# param map : list : carte a afficher
#       filename : string : nom du fichier de sauvegarde 
def save(map,filename):
    # Ouverture de l'ecriteur de fichier
    f = open(filename + ".pgm", "w")
    f.write("P2\n")
    f.write("# Carte salle AVR\n")
    f.write("56 72\n")
    f.write("3\n")
    # Ecriture de la map dans le fichier 
    s = ""
    for i in range(len(map)):
        for j in range(len(map[0])):
            s = s + str(map[i][j]) + " "
        s = s + "\n"
    f.write(s)
    # Fermeture du fichier 
    f.close

# Methode qui permet de sauvegarder la carte passe en parametre
# param map : list : carte a afficher
#       filename : string : nom du fichier de sauvegarde 
def exportMap(map,filename):
    # Ouverture de l'ecriteur de fichier
    f = open(filename + ".pgm", "w")
    f.write("P2\n")
    f.write("# Carte salle AVR\n")
    f.write("112 144\n")
    f.write("2\n")
    # Ecriture de la map dans le fichier 
    s = ""
    for i in range(len(map)):
        ligne = ""
        for j in range(len(map[0])):
            s = s + str(map[i][j]) + " " + str(map[i][j]) + " "
            ligne = ligne + str(map[i][j]) + " " + str(map[i][j]) + " "
        s = s + "\n"
        s = s + ligne + "\n"
    f.write(s)
    # Fermeture du fichier 
    f.close

# Methode qui permet un affichage console de la carte passe en parametre
# param map : list : carte a afficher 
def afficher(map):
    s = "Affichage de la carte \n"
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] == float('inf') or map[i][j] == -1 * float('inf'):
                s = s + "I"
            else:
                if map[i][j] != -1:
                    s = s + str(int(map[i][j]))
                else:
                    s = s + 'X'
        s = s + "\n"
    print(s)

# Methode qui permet un affichage console de la carte passe en parametre avec le chemin represente par des points
# param map : list : carte a afficher
#       path : list : chemin a afficher
def printPath(map,path):
    pmap = copy.deepcopy(map)
    for p in path:
        pmap[p[0]][p[1]] = '.'
    s = "Affichage de la carte \n"
    for i in range(len(pmap)):
        for j in range(len(pmap[0])):
            if pmap[i][j] == float('inf') or pmap[i][j] == -1 * float('inf'):
                s = s + "I"
            else:
                s = s + str(pmap[i][j])
        s = s + "\n"
    print(s)

# Methode qui creer l'espace de configuration 
# param map : list : carte a utiliser pour creer l'espace de configuration 
# retrn : list : carte representant l'espace de configuration  
def espaceDeConfig(map):
    print("Creation de l'espace de configuration")
    # Recuperation de la dilatation de la carte 
    dilatation = dilateur.binary_dilation(map, iterations = rayonPepper)
    # Mise a jour de la carte pour recuperer l'espace de configuration
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] == 0 and dilatation[i][j]:
                map[i][j] = 1
    return map

# Methode qui retourne la valeur de l'heuristique pour le point s ici la distance de Manhatan
# param s1 : tuple : position 
#       s2 : tuple : position 
# return : float : distance euclidienne entre s et le start
def heuristique(s1,s2):
    return np.abs(s2[0] - s1[0]) + np.abs(s2[1] - s1[1])

def distanceAuBord(map): 
    dmap = copy.deepcopy(map)
    for x in range(len(dmap)):
        for y in range(len(dmap[0])):
            if dmap[x][y] < 0:
                dmap[x][y] = -1
            else : 
                dmap[x][y] = 255
    size = 3
    for x in range(len(dmap)):
        for y in range(len(dmap[0])):
            if dmap[x][y] >= 0:
                #print(dmap[x-1][y-1], dmap[x][y-1], dmap[x+1][y-1], dmap[x][y-1],min(dmap[x-1][y-1], dmap[x][y-1], dmap[x+1][y-1], dmap[x][y-1]))
                dmap[x][y] = min(1+dmap[x-1][y-1], 1+dmap[x][y-1], 1+dmap[x+1][y-1], 1+dmap[x-1][y], dmap[x][y])
    
    for x in range(len(dmap)-1, 0, -1):
        for y in range(len(dmap[0])-1, 0, -1):
            if dmap[x][y] >= 0:
                dmap[x][y] = min(dmap[x][y],1+dmap[x+1][y], 1+dmap[x+1][y+1], 1+dmap[x][y+1], 1+dmap[x-1][y+1])
    return dmap

# Methode qui retourne les successeur du point donne en parametre
# param s : tuple : position a trouver les voisin 
#       map : list : carte ou on se deplace 
#table1 = [58*2,10]
def succ(s, map):
    l = []
    for i in range (-1,2):
        for j in range (-1,2):
            if(s[0]+i>0 and s[0]+i<len(map[0]) and s[1]+j>0 and s[1]+j<len(map) and map[s[0]+i][s[1]+j]==0):
                l.append((s[0]+i,s[1]+j))
    return l

# Methode qui cree un chemin de start a goal dans la carte map
# param map : liste : carte ou on se deplace
#       start : tuple : position de depart 
#       goal : tuple : position d'arrivee
# return path : list : succession de position pour aller de start a goal
def vague(map,start,goal):
    # Initialisation 
    h = []
    vmap = copy.deepcopy(map)
    hmap = copy.deepcopy(map)
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] != 0: 
                vmap[i][j] = -1 * float('inf')
    dmap = distanceAuBord(vmap)
    # Calcul du chamin 
    heap.heappush(h,(0,start))
    s = heap.heappop(h)
    print(start)
    while not (s[1][0] == goal[0] and s[1][1] == goal[1]):
        suc = []
        # Voisin voisinage 4 
        if vmap[s[1][0]+1][s[1][1]] == 0 and start != [s[1][0]+1,s[1][1]]: suc.append((s[1][0]+1,s[1][1]))
        if vmap[s[1][0]-1][s[1][1]] == 0 and start != [s[1][0]-1,s[1][1]]: suc.append((s[1][0]-1,s[1][1]))
        if vmap[s[1][0]][s[1][1]+1] == 0 and start != [s[1][0],s[1][1]+1]: suc.append((s[1][0],s[1][1]+1))
        if vmap[s[1][0]][s[1][1]-1] == 0 and start != [s[1][0],s[1][1]-1]: suc.append((s[1][0],s[1][1]-1))
        for sp in suc:
            vmap[sp[0]][sp[1]] = vmap[s[1][0]][s[1][1]] + 1
            hmap[sp[0]][sp[1]] = heuristique(sp,goal)
            heap.heappush(h,(vmap[sp[0]][sp[1]] + hmap[sp[0]][sp[1]] - dmap[sp[0]][sp[1]],sp))
        s = heap.heappop(h)
    # Reconstruction du chamin 
    way = [(s[1][0],s[1][1])]
    s = s[1]
    while not (s[0] == start[0] and s[1] == start[1]):
        suc = []
        # Voisinage 4
        if vmap[s[0]+1][s[1]] != 0 or (vmap[s[0]+1][s[1]] == 0 and start == [s[0]+1,s[1]]): suc.append((s[0]+1,s[1]))
        if vmap[s[0]-1][s[1]] != 0 or (vmap[s[0]-1][s[1]] == 0 and start == [s[0]-1,s[1]]): suc.append((s[0]-1,s[1]))
        if vmap[s[0]][s[1]+1] != 0 or (vmap[s[0]][s[1]+1] == 0 and start == [s[0],s[1]+1]): suc.append((s[0],s[1]+1))
        if vmap[s[0]][s[1]-1] != 0 or (vmap[s[0]][s[1]-1] == 0 and start == [s[0],s[1]-1]): suc.append((s[0],s[1]-1))
        # Voisinage 8
        if vmap[s[0]+1][s[1]+1] != 0 or (vmap[s[0]+1][s[1]+1] == 0 and start == [s[0]+1,s[1]+1]): suc.append((s[0]+1,s[1]+1))
        if vmap[s[0]+1][s[1]-1] != 0 or (vmap[s[0]+1][s[1]-1] == 0 and start == [s[0]+1,s[1]-1]): suc.append((s[0]+1,s[1]-1))
        if vmap[s[0]-1][s[1]+1] != 0 or (vmap[s[0]-1][s[1]+1] == 0 and start == [s[0]-1,s[1]+1]): suc.append((s[0]-1,s[1]+1))
        if vmap[s[0]-1][s[1]-1] != 0 or (vmap[s[0]-1][s[1]-1] == 0 and start == [s[0]-1,s[1]-1]): suc.append((s[0]-1,s[1]-1))
        minimum = 0
        vmin = float('inf')
        for sp in suc:
            if vmap[sp[0]][sp[1]] < vmin and vmap[sp[0]][sp[1]] >= 0:
                minimum = sp
                vmin = vmap[sp[0]][sp[1]]
        s = minimum
        way.insert(0,s)
    return way

def pathToMove(path, robot):
    # 4 3 2 
    # 5   1 
    # 6 7 8 
    orient = robot.position.theta + 3.14
    pos = path[0]
    waypoint = path[1]
    print(pos ,waypoint, orient)
    #changement axe du y (-(waypoint[0]-pos[0]))
    desired = math.atan2(-(waypoint[0]-pos[0]),waypoint[1]-pos[1])
    rotation = desired - orient
    rotation = np.degrees(rotation)
    if rotation > 180:
        rotation = rotation - 360
    print(rotation)
    robot.moveRobot(0,0,rotation)
    
    #desired = orient
    #if waypoint[0] < pos[0]: # 4 5 6 
    #    if waypoint[1] < pos[1]: # 4
    #        desired = 6
    #    if waypoint[1] == pos[1]: # 5
    #        desired = 7
    #    if waypoint[1] > pos[1]: # 6
    #        desired = 8
    #if waypoint[0] == pos[0]: # 3   7
    #    if waypoint[1] < pos[1]: # 3
    #        desired = 5
    #    if waypoint[1] > pos[1]: # 7
    #        desired = 1
    #if waypoint[0] < pos[0]: # 2 1 8
    #    if waypoint[1] < pos[1]: # 2
    #        desired = 4
    #    if waypoint[1] == pos[1]: # 1
    #        desired = 3
    #    if waypoint[1] > pos[1]: # 8
    #        desired = 2
    #print(desired,orient)
    # On s'oriente
    #if ((abs((desired) - (orient))) * 45) > 180:
    #    print("hey",0,0,360-((abs((desired) - (orient))) * 45))
    #    robot.moveRobot(0,0,360-((abs((desired) - (orient))) * 45))
    #else:
    #    print(0,0,((abs((desired) - (orient))) * 45))
    #    robot.moveRobot(0,0,((abs((desired) - (orient))) * 45))
    # On se deplace
    #print(0.05,0,0)
    robot.moveRobot(0.1,0,0)
    orient = desired
    pos = waypoint

# ---------------------------------- MAIN ---------------------------------- #
map = []
map = loadMap("Salle_AVR_ClosedDoor_NoChair.pgm")
map = espaceDeConfig(map)
save(map,"Config_Salle_AVR_ClosedDoor_NoChair")
exportMap(map,"Config_Double_Salle_AVR_ClosedDoor_NoChair")
#map = loadMap("Config_Double_Salle_AVR_ClosedDoor_NoChair.pgm")

#afficher(map)

#getPath(map,[4,4],[60,5])

#porte = [60*2,42*2]
#tableau = [7*2,7*2]
#table1 = [58*2,10]
#table2 = [58*2,22*2]
#table3 = [58*2,34*2]
#table4 = [31*2,10*2]
#table5 = [31*2,22*2]
#table6 = [31*2,34*2]
#table7 = [21*2,16*2]
#table8 = [21*2,28*2]
#testPoint = [44*2,44*2]

porte = [60,42]
tableau = [7,7]
table1 = [58,10]
table2 = [58,22]
table3 = [58,34]
table4 = [31,10]
table5 = [31,22]
table6 = [31,34]
table7 = [21,16]
table8 = [21,28]
testPoint = [44,44]

path = vague(map,porte,table7)
#printPath(map,path)

print("Waypoint : 0, 1, 2, 3, 4, 5, 6, 7, 8, 9")
dfrom = input("From : ")
dto = input("To : ")
if dfrom == 0: dfrom = porte
if dfrom == 1: dfrom = table1
if dfrom == 2: dfrom = table2
if dfrom == 3: dfrom = table3
if dfrom == 4: dfrom = table4
if dfrom == 5: dfrom = table5
if dfrom == 6: dfrom = table6
if dfrom == 7: dfrom = table7
if dfrom == 8: dfrom = table8
if dfrom == 9: dfrom = testPoint
if dto == 0: dto = porte
if dto == 1: dto = table1
if dto == 2: dto = table2
if dto == 3: dto = table3
if dto == 4: dto = table4
if dto == 5: dto = table5
if dto == 6: dto = table6
if dto == 7: dto = table7
if dto == 8: dto = table8
if dto == 9: dto = testPoint

path = vague(map,dfrom,dto)
printPath(map,path)

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
    #mat.start()
    toto = input("GO? ")
    #mat.moveRobot(1.8,0,0)
    dact = dfrom
    while dact != dto:
        pathToMove(path, mat)
        #print(mat.initPosition,mat.position)
        posx = mat.position.x - mat.initPosition.x
        posy = mat.position.y - mat.initPosition.y
        #print(posx,posy)
        #print (int(posx * 100 / 5), int(posy * 100 / 5))
        dact[0] = dfrom[0] + int(posy * 100 / 10)
        dact[1] = dfrom[1] - int(posx * 100 / 10)
        path = vague(map,dact,dto)
        printPath(map,path)
        #dact = dto
    mat.stopRobot()
    print("FIN ROBOT")
except rospy.ROSInterruptException:
    pass


