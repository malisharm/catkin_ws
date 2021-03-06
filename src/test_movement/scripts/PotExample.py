#!/usr/bin/env python

import rospy

import test_movement
import PotentialFieldBrain

import cv2
import numpy
import time

import math
import random


class KeepMoving(PotentialFieldBrain.PotentialFieldBehavior):
    """This is a brain-dead class that just reports a fixed magnitude and a heading that
    matches the robot's current heading"""

    def update(self):
        """set zero magnitude and current heading"""
        self.setVector(0.2, 0.0)

class ObstacleForce(PotentialFieldBrain.PotentialFieldBehavior):

    def __init__(self, posPercent, speedMult):
        # posPercent is distance from left side of camera image, in percent of botWidth (from 0 to 1)
        self.speedMult = speedMult
        self.imageWidth = 30
        self.angle = (posPercent-0.5)*60
        self.imageLeft = (640*posPercent)-(self.imageWidth/2)
        self.imageRight = self.imageLeft+self.imageWidth
        if self.imageRight > 640:
            self.imageLeft -= self.imageRight-640
            self.imageRight = 640
        elif self.imageLeft < 0:test_movement.TurtleBot()
            self.imageRight += 0-self.imageLeft
            self.imageLeft = 0

    def update(self):
        # botWidth = 640
        # botHeight = 480

        obstVals = self.robot.getDepth(self.imageLeft,
                                       240-(self.imageWidth/2),
                                       self.imageWidth,
                                       self.imageWidth)

        masked_obstVals = numpy.ma.masked_array(obstVals, obstVals==0)
        # print numpy.ma.masked_array(obstVals, obstVals==0)

        meanDistance = numpy.mean(masked_obstVals)

	    #print "--------"
        #print masked_obstVals
        #print meanDistance
        #print (50/meanDistance, 180-(self.angle))

        if meanDistance < 1500:
            if meanDistance < 500:
                meanDistance = 500
            self.setVector(self.speedMult/meanDistance, 180-(self.angle))
            #self.setVector(0.0, 0.0)
            # print self.angle
        else:
            self.setVector(0.0, 0.0)


class DisplayCamera(PotentialFieldBrain.PotentialFieldBehavior):

    def __init__(self):
        cv2.namedWindow("name", 1)

    def update(self):
        # botWidth = 640
        # botHeight = 480

        image = self.robot.getImage()
        cv2.imshow("name", image)
        cv2.waitKey(1)

        self.setVector(0.0, 0.0)

# -----------------------------------------------------
# Run the demo using something like this:

def runDemo(runtime = 120):
    brain = setupPot()
    brain.add( KeepMoving() )
    for i in range(10, 90, 10):
        brain.add( ObstacleForce(i/100.0, 10) )
    brain.add( DisplayCamera() )

    timeout = time.time()+runtime
    while time.time() < timeout and not rospy.is_shutdown():
        rospy.sleep(0.1)
        print("======================================")
        brain.step()

    brain.stopAll()





def setupPot(robotCode = None):
    """Helpful function takes optional robot code (the six-digit Fluke board number). If code
    is given, then this connects to the robot. Otherwise, it connects to a simulated robot, and
    then creates a SubsumptionBrain object and returns it."""

    currRobot = test_movement.TurtleBot()
    currBrain = PotentialFieldBrain.PotentialFieldBrain(currRobot)
    return currBrain

if __name__=="__main__":
  rospy.init_node('PotExample')
  runDemo(120)

