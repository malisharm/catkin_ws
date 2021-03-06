
""" lets you check location tags around a specific x,y coordinate."""

import os
# import time

import cv2
import numpy as np
import readMap


def main(mapFile):
    mapImg = getOlinMap(mapFile)
    (mapHgt, mapWid, mapDep) = mapImg.shape
    setupWindows()
    lineTemplate = "{0:d} {1:.2f} {2:.2f} {3:d}\n"
    # the node you want to look for points near
    #nearby =  [20.0, 40.1]

    locX = float(raw_input("Please type in x coordinate."))
    locY = float(raw_input("Please type in y coordinate."))
    locH = float(raw_input("Please type in heading angle."))

    while True:
        nextMapImg = mapImg.copy()
        (pixX, pixY) = convertWorldToMap(locX, locY, mapWid, mapHgt)
        drawPosition(nextMapImg, pixX, pixY, locH, (255, 0, 0))
        posInfo = "(" + str(locX) + ", " + str(locY) + ", " + str(locH) + ")"
        cv2.putText(nextMapImg, posInfo, (40, 40), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 0, 0), 2)
        cv2.imshow("Map", nextMapImg)
        res = cv2.waitKey()
        userKey = chr(res % 0xFF)
        if userKey == 'q':
            break
        elif userKey == 'w':
            locX += 0.1
        elif userKey == 's':
            locX -= 0.1
        elif userKey == 'a':
            locY += 0.1
        elif userKey == 'd':
            locY -= 0.1
        elif userKey == 'z':
            locH += 45
            if locH >= 360:
                locH -= 360
        elif userKey == 'c':
            locH -= 45
            if locH < 0:
                locH += 360




def getOlinMap(mapFilename):
    """Read in the Olin Map and return it. Note: this has hard-coded the orientation flip of the particular
    Olin map we have, which might not be great, but I don't feel like making it more general. Future improvement
    perhaps."""
    origMap = readMap.createMapImage(mapFilename, 20)
    map2 = np.flipud(origMap)
    olinMap = np.rot90(map2)
    return olinMap


def readLocations(locFile):
    locations = {}
    f = open(locFile)
    for line in f.readlines():
        line = line.rstrip('/n')
        line = line.split()
        locations[int(line[0])] = [float(line[1]), float(line[2]), int(line[3])]
    return locations


def setupWindows():
    """Creates three windows and moves them to the right places on screen."""
    cv2.namedWindow("Map")
    cv2.moveWindow("Map", 700, 50)


def drawPosition(image, x, y, heading, color):
    cv2.circle(image, (x, y), 6, color, -1)
    newX = x
    newY = y
    if heading == 0:
        newY = y - 10
    elif heading == 45:
        newX = x - 8
        newY = y - 8
    elif heading == 90:
        newX = x - 10
    elif heading == 135:
        newX = x - 8
        newY = y + 8
    elif heading == 180:
        newY = y + 10
    elif heading == 225:
        newX = x + 8
        newY = y + 8
    elif heading == 270:
        newX = x + 10
    elif heading == 315:
        newX = x + 8
        newY = y - 8
    else:
        print "Error! The heading is", heading
    cv2.line(image, (x, y), (newX, newY), color)


def convertMapToWorld(mapX, mapY, mapWid, mapHgt):
    """Converts coordinates in pixels, on the map, to coordinates (real-valued) in
    meters. Note that this also has to adjust for the rotation and flipping of the map."""
    # First flip x and y values around...
    flipY = mapWid - 1 - mapX
    flipX = mapHgt - 1 - mapY
    # Next convert to meters from pixels, assuming 20 pixels per meter
    mapXMeters = flipX / 20.0
    mapYMeters = flipY / 20.0
    return mapXMeters, mapYMeters


def convertWorldToMap(worldX, worldY, mapWid, mapHgt):
    """Converts coordinates in meters in the world to integer coordinates on the map
    Note that this also has to adjust for the rotation and flipping of the map."""
    # First convert from meters to pixels, assuming 20 pixels per meter
    pixelX = worldX * 20.0
    pixelY = worldY * 20.0
    # Next flip x and y values around
    mapX = mapWid - 1 - pixelY
    mapY = mapHgt - 1 - pixelX
    return int(mapX), int(mapY)


def extractNum(fileString):
    """finds sequence of digits"""
    numStr = ""
    foundDigits = False
    for c in fileString:
        if c in '0123456789':
            foundDigits = True
            numStr += c
        elif foundDigits:
            break
    if numStr != "":
        return int(numStr)
    else:
        return -1

if __name__ == '__main__':
    main("olinNewMap.txt")
