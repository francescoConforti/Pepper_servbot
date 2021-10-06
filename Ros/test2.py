
class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self, False)
        self.motion = ALProxy("ALMotion")
        self.positionErrorThresholdPos = 0.01
        self.positionErrorThresholdAng = 0.03

    def onLoad(self):
        pass

    def onUnload(self):
        self.motion.moveToward(0.0, 0.0, 0.0)

    def onInput_onStart(self, X, Y, Deg):
        import almath
        # The command position estimation will be set to the sensor position
        # when the robot starts moving, so we use sensors first and commands later.
        initPosition = almath.Pose2D(self.motion.getRobotPosition(True))
        targetDistance = almath.Pose2D(self.getParameter("Distance X (m)"),
            self.getParameter("Distance Y (m)"),
            self.getParameter("Theta (deg)") * almath.PI / 180)
        expectedEndPosition = initPosition * targetDistance
        enableArms = self.getParameter("Arms movement enabled")
        self.motion.setMoveArmsEnabled(enableArms, enableArms)
        self.motion.moveTo(X,Y,Deg * almath.PI / 180)

        # The move is finished so output
        realEndPosition = almath.Pose2D(self.motion.getRobotPosition(False))
        positionError = realEndPosition.diff(expectedEndPosition)
        positionError.theta = almath.modulo2PI(positionError.theta)
        if (abs(positionError.x) < self.positionErrorThresholdPos
            and abs(positionError.y) < self.positionErrorThresholdPos
            and abs(positionError.theta) < self.positionErrorThresholdAng):
            self.onArrivedAtDestination()
        else:
            self.onStoppedBeforeArriving(positionError.toVector())

    def onInput_onStop(self):
        self.onUnload()
