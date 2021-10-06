#!/usr/bin/python
# -*- coding: utf-8 -*-

import qi

behavior_name = "myBehavior"
package_name = "myApplication"
package_id = "choregraphe-520c35"
ip = "100.75.166.171"
# La communication sur le robot passe par le port 9559, en simulation,
# dans certains cas, il est necessaire de le changer
port = 9559

class Main():

     def __init__(self, ip, port):
        self.session = qi.Session()
        try:
            self.session.connect("tcp://" + ip + ":" + str(port))
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + ip + "\" on port " + str(port) +".\n")
            sys.exit(1)
            
        # self.tts = self.session.service("ALTextToSpeech")
        self.almemory = self.session.service("ALMemory")
        self.behavior_mng_service = self.session.service("ALBehaviorManager")
        self.tabletService = self.session.service("ALTabletService")

     def start(self):        
          # Launch behavior
          # Check that the behavior exists
          try:
               if(self.behavior_mng_service.isBehaviorInstalled(behavior_name)):
                    # Check that it is not already running.
                    if(not self.behavior_mng_service.isBehaviorRunning(behavior_name)):
                         # Launch behavior. This is a blocking call, use _async=True if you do not
                         # want to wait for the behavior to finish.
                         self.behavior_mng_service.runBehavior(behavior_name, _async=True)
                    else:
                         print "Behavior is already running."
          except Exception as e:
               print "Error was: " + str(e)
               self.tabletService.hideWebview()
               self.tabletService.cleanWebview()
               self.behavior_mng_service.stopBehavior(behavior_name)
               sys.exit(1)
        
          # self.almemory.subscriber("menu").signal.connect(self.on_menu)
          self.almemory.subscriber("goTable").signal.connect(self.on_goTable)

          # Display the index.html page of a behavior name j-tablet-browser
          # The index.html must be in a folder html in the behavior folder
          # if self.tabletService.loadApplication(package_id):
          #     print "Application loaded"
          #     self.tabletService.showWebview()

     def stop(self):
          self.tabletService.hideWebview()
          self.tabletService.cleanWebview()
          self.behavior_mng_service.stopBehavior(behavior_name)

     # def on_menu(self, value):
     #      if(value):
     #           self.tabletService.showWebview("http://" + self.tabletService.robotIp() + "/apps/" + package_name + "/menu_2.html")

     def on_goTable(self, value):
          pass    

if __name__ == '__main__':
    main = Main(ip, port)
    main.start()
    raw_input("Press Enter when finished :")
    main.stop()
