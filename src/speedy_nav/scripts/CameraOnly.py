#!/usr/bin/env python

#from roslib import message

import cv2
import rospy
import threading
import math
import sys

from std_msgs.msg import String

from datetime import datetime

import cv2
from cv_bridge import CvBridge, CvBridgeError

import numpy

from sensor_msgs.msg import Image


def getMedianAngle(leftDist, rightDist, angleBetween):
	"""Given two distances and the angle between them, finds the angle of the observer to the surface with flat against the wall facing left being zero."""
	if leftDist <= rightDist:
		shorter, longer = leftDist, rightDist
	else:
		shorter, longer = rightDist, leftDist

	shorter = float(shorter)
	longer = float(longer)
	angleBetween = float(math.radians(angleBetween))

	#Uses law of cosines to determine length of wall spanned by sensor
	wallDist = math.sqrt(math.pow(shorter,2) + math.pow(longer,2)
		- 2 * shorter * longer * math.cos(angleBetween))

	if wallDist <= 0:
		return 90

	#Uses law of sines to determine angle between wall and the shorter distance
	angleShort = math.asin(math.sin(angleBetween) * longer / wallDist)

	#Uses law of cosines to determine the length of median
	halfWall = wallDist / 2.0
	medianDist = math.sqrt(math.pow(shorter, 2) + math.pow(halfWall, 2)
		- 2 * shorter * halfWall * math.cos(angleShort))

	#Uses law of sines to determine the angle of the median to the wall
	medianAngle = math.asin(math.sin(angleShort) * shorter / medianDist)

	medianAngle = math.degrees(medianAngle)
	print medianAngle
	if leftDist < rightDist:
		medianAngle = 180 - medianAngle

	return medianAngle



class ImageSensor():
	def __init__(self):
		self.bridge = CvBridge()
		#self.image_sub = rospy.Subscriber("/camera/rgb/image_color",Image,self.image_callback)
		self.image_sub = rospy.Subscriber("/camera/image_decompressed",Image, self.image_callback)
		cv2.namedWindow("TurtleCam", 1)

	def image_callback(self, data):
		try:
			cv_image = self.bridge.imgmsg_to_cv2(data, "passthrough")
		except CvBridgeError, e:
			print e


		############## Temporary ##############

		height, width, depth = cv_image.shape
		sectionWidth = width / 20
		# box = c,r,w,h

		copy = cv_image.copy()
		for x in range(21):
			cv2.rectangle(cv_image, (x * sectionWidth, 0),(sectionWidth, height),(20,20,200))
#		cv2.rectangle(cv_image, (leftBox[0], leftBox[1]),(leftBox[0] + sectionWidth, leftBox[1] + sectionHeight),(30,30,200))
#		cv2.rectangle(cv_image, (rightBox[0], rightBox[1]),(rightBox[0] + sectionWidth, rightBox[1] + sectionHeight),(30,30,200))

		#######################################

		cv2.imshow("TurtleCam", cv_image)

		code = chr(cv2.waitKey(10) & 255)
		if code == 'c':
				cv2.imwrite("/home/macalester/catkin_ws/src/speedy_nav/res/captures/cap-" + str(datetime.now()) + ".jpg", cv_image)

	def exit(self):
		self.image_sub.unregister()


class DepthSensor( threading.Thread):
	def __init__(self):
		print "sensor thread init"
		threading.Thread.__init__(self)
		self.lock = threading.Lock()
		self.bridge = CvBridge()

		self.depth_array = None
		self.depth_sub = rospy.Subscriber("/camera/depth_decompressed", Image, self.depth_callback)

		self.runFlag = True

	def run(self):
		with self.lock:
			self.runFlag = True
		runFlag = True

		while runFlag:
			rospy.sleep(0.1)
			with self.lock:
				runFlag = self.runFlag
		self.depth_sub.unregister()


	def depth_callback(self, data):
		with self.lock:
			self.depth_array = data

	def getDims(self):
		with self.lock:
			data = self.depth_array
		if data == None:
			return 0,0
		#print "Width: ", botWidth, " Height: ", botHeight
		return data.width, data.height


	def getDepth(self, x, y, width, height):
		with self.lock:
			data = self.depth_array
		try:
			if data == None:
				sys.stdout.write("Waiting for depth data")
				while data == None:
					sys.stdout.write(".")
					sys.stdout.flush()
					if rospy.is_shutdown():
				ls		return
					rospy.sleep(0.1)
					with self.lock:
						data = self.depth_array
				print " Done!"
			cv_image = self.bridge.imgmsg_to_cv2(data, "passthrough")
		except CvBridgeError, e:
			print e
		numpy_array = numpy.asarray(cv_image)
		retval = numpy_array[y:y+height, x:x+width]
		return retval


	def showDepthImage(self):
		with self.lock:
			data = self.depth_array
		if data == None:
			return
		cv_image = self.bridge.imgmsg_to_cv2(data, "passthrough")
		cv2.imshow("Depth Data", cv_image)

	def exit(self):
		print "image sensor shutdown received"
		with self.lock:
			self.runFlag = False



class TurtleBot:

	def __init__(self):
		self.imageControl = ImageSensor()
		self.imageControl.start()
		#self.depthSensor = DepthSensor()
		#self.depthSensor.start()

	def findAngleToWall(self):
		width, height = self.depthSensor.getDims()
		sectionWidth = width / 30.0
		sectionHeight = height / 5.0
		# box = c,r,w,h
		leftBox = int(sectionWidth * 10), int(sectionHeight * 2), int(sectionWidth), int(sectionHeight)
		rightBox = int(sectionWidth * 19), int(sectionHeight * 2), int(sectionWidth), int(sectionHeight)

		leftDist = numpy.mean(self.depthSensor.getDepth(*leftBox))
		rightDist = numpy.mean(self.depthSensor.getDepth(*rightBox))
		return getMedianAngle(leftDist, rightDist, angleBetween = 11.0)

	def run(self):
		while True:
			cv2.waitKey(200)
			#cv2.imshow
			#self.depthSensor.showDepthImage()
			#print self.findAngleToWall()

	def exit(self):
		print("************** RECEIVED ON SHUTDOWN **************")
		cv2.destroyAllWindows()
		self.imageControl.exitS()
		#self.depthSensor.exit()

if __name__=="__main__":

	rospy.init_node('CameraOnly')
	controller = TurtleBot()
	controller.run()
	rospy.on_shutdown(controller.exit)
	rospy.spin()


