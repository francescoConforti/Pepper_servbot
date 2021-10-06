#!/usr/bin/python
# -*- coding: utf-8 -*-


from naoqi import ALProxy
import time 

ip = "100.75.166.171"
port = 9559         # La communication sur le robot passe par le port 9559, en simulation,
                    # dans certains cas, il est necessaire de le changer

class Main():

    def __init__(self, ip, port):
        #self.tts = ALProxy("ALTextToSpeech", ip, port)
        self.al = ALProxy("ALLeds", ip, port)

    def start(self):
        #self.tts.say("Bonjour ! Je suis là pour t'aider. Apprend moi quelque chose ?")

        ## Allumage des LEDs de l'oreille gauche de Pepper
        for i in range(10):
            self.al.on("LeftEarLed"+str(i+1))
            # time.sleep(10)
            # self.al.off("LeftEarLed"+i)

            

if __name__ == '__main__':
    main = Main(ip, port)
    main.start()
