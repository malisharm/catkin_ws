#!/usr/bin/env python

import rospy

import test_movement
import SubsumptionBrain

import numpy
import time

import math
import random


class Straight(SubsumptionBrain.SubsumptionBehavior):

    def update(self):
        """This behavior ignores sensors, and just goes in a slow circle"""
        self.setSpeeds(0.15, 0.0)
        self.setFlag()


class AvoidWalls(SubsumptionBrain.SubsumptionBehavior):

    def update(self):
        """This behavior turns when an obstacle is detected"""

        # botWidth = 640
        # botHeight = 480
        obstVals = self.robot.getDepth(70, 220, 500, 40)

        print obstVals[20, 250] # y, x

        masked_obstVals = numpy.ma.masked_array(obstVals, obstVals==0)
        # print numpy.ma.masked_array(obstVals, obstVals==0)

        left_side = numpy.mean(masked_obstVals[0:40, 0:40])
        right_side = numpy.mean(masked_obstVals[0:40, -40:])

        if left_side < 850 and right_side < 850:
            speed = -0.1
        else:
            speed = 0
        if left_side < 850 or right_side < 850:
            if left_side < right_side:
                # left side closer
                self.setSpeeds(speed, -0.7)
            else:
                # right side closer
                self.setSpeeds(speed, 0.7)
            self.setFlag()

class SensorDebug(SubsumptionBrain.SubsumptionBehavior):

    def update(self):
        """This behavior stops movement, displays sensor info"""
        self.setSpeeds(0.0, 0.0)

	# botWidth = 640
        # botHeight = 480
        obstVals = self.robot.getDepth(70, 220, 500, 40)

        print obstVals[249:251, 19:21]
        self.setFlag()


# -----------------------------------------------------
# Run the demo using something like this:


def runDemo(runtime = 120):
    """This function is really a model to be modified.  It shows how to take a SubsumptionBrain
    and an optional time, add behaviors to the brain, and then run it for the given time."""
    brain = setupSubsumption()
    # add behaviors, in order from lowest to highest
    brain.add( Straight() )
    brain.add( AvoidWalls() )
    # brain.add( SensorDebug() )

    timeout = time.time()+runtime
    while time.time() < timeout and not rospy.is_shutdown():
        brain.step()
        rospy.sleep(0.2)

    brain.stopAll()



def setupSubsumption(robotCode = None):
    """Helpful function takes optional robot code (the six-digit Fluke board number). If code
    is given, then this connects to the robot. Otherwise, it connects to a simulated robot, and
    then creates a SubsumptionBrain object and returns it."""

    currRobot = test_movement.TurtleBot()
    currBrain = SubsumptionBrain.SubsumptionBrain(currRobot)
    return currBrain

if __name__=="__main__":
  rospy.init_node('SubExample')
  runDemo(120)
