# Author: Aleksandr Parfenov
# The Polygon Map Generator, based on article "Polygonal Map Generation for Games" from "Red Blob Games"
# http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/

import random
import math
from PIL import Image
from scipy.spatial import Delaunay
from collections import defaultdict
import itertools

class Point:
    """ Point class represents and manipulates x,y coords. """

    def __init__(self, x, y):
        """ Create a new point at the origin """
        self.x = x
        self.y = y

    def length(self):
    	return math.sqrt(self.x * self.x + self.y * self.y)

# radialRandomBumps = 0
# radialRandomStartAngle = 0
# radialRandomDipAngle = 0
# raidalRandomDipWidth = 0
ISLAND_FACTOR = 1.07 # 1.0 - No small islands, 2.0 - a lot of small islands

# def configureRadialRandom():
radialRandomBumps = random.randint(1, 6)
radialRandomStartAngle = random.uniform(0, 2 * math.pi)
radialRandomDipAngle = random.uniform(0, 2 * math.pi)
raidalRandomDipWidth = random.uniform(0.2, 0.7)

neiList=defaultdict(set)
mapWidth, mapHeight = 1024, 1024
mapMatrix = [[0 for x in range(mapWidth)] for y in range(mapHeight)]
num_cells = 700
nx = []
ny = []
polygonType = []
polygonDepth = []
polygonMoisture = []

def radialRandomIsInside(point):
	angle = math.atan2(point.x, point.y)
	length = 0.5 * (max(abs(point.x), abs(point.y)) + point.length())

	r1 = 0.5 + 0.4 * math.sin(radialRandomStartAngle + radialRandomBumps * angle + math.cos((radialRandomBumps + 3)*angle))
	r2 = 0.7 + 0.2 * math.sin(radialRandomStartAngle + radialRandomBumps * angle + math.sin((radialRandomBumps + 2)*angle))

	if abs(angle - radialRandomDipAngle) < raidalRandomDipWidth or abs(angle - radialRandomDipAngle + 2*math.pi) < raidalRandomDipWidth or abs(angle - radialRandomDipAngle - 2*math.pi) < raidalRandomDipWidth:
		r1 = r2 = 0.2

	return (length < r1 or (length > r1 * ISLAND_FACTOR and length < r2));

def generateVoronoiDiagram():
	for i in range(num_cells):
		nx.append(random.randrange(mapWidth))
		ny.append(random.randrange(mapHeight))
	for y in range(mapHeight):
		for x in range(mapWidth):
			dmin = math.hypot(mapWidth-1, mapHeight-1)
			j = -1
			for i in range(num_cells):
				d = math.hypot(nx[i]-x, ny[i]-y)
				if d < dmin:
					dmin = d
					j = i
			mapMatrix[x][y] = j

def generatePolygonsMap():
	waterPixles = []
	soilPixels = []
	for i in range(num_cells):
		waterPixles.append(0)
		soilPixels.append(0)
		polygonType.append(0)
		polygonDepth.append(0)
		polygonMoisture.append(0)
	for y in range(mapHeight):
		for x in range(mapWidth):
			normal_x = (x - mapWidth/2) / (mapWidth/2)
			normal_y = (y - mapHeight/2) / (mapHeight/2)
			i = mapMatrix[x][y]
			if radialRandomIsInside(Point(normal_x, normal_y)):
				soilPixels[i] = soilPixels[i] + 1
			else:
				waterPixles[i] = waterPixles[i] + 1
	for i in range(num_cells):
		if waterPixles[i] > soilPixels[i]:
			polygonType[i] = 0
			polygonDepth[i] = 0
			polygonMoisture[i] = 1.0
		else:
			polygonType[i] = 1
			polygonDepth[i] = 999
			polygonMoisture[i] = 0.0
	for i in range(15):
		polygonMoisture[random.randint(0, num_cells - 1)] = random.uniform(0.0, 3.0)

def voronoiScipy():
	points = []
	for i in range(num_cells):
		points.append([nx[i], ny[i]])

	tri = Delaunay(points)
	for p in tri.vertices:
		for i, j in itertools.combinations(p, 2):
			neiList[i].add(j)
			neiList[j].add(i)

def fillPolygonTypes():
	for i in range(num_cells):
		adjacentSoil = 0
		adjacentWater = 0
		for adjacentI in neiList[i]:
			if polygonType[adjacentI] == 0:
				adjacentWater = adjacentWater + 1
			else:
				adjacentSoil = adjacentSoil + 1
		if adjacentWater == 0 and polygonType[i] != 0:
			polygonType[i] = 2
		elif polygonType[i] == 1:
			polygonDepth[i] = 1
	for i in range(num_cells):
		adjacentMin = 999
		minJ = i
		moistureSum = 0.0
		for adjacentJ in neiList[i]:
			moistureSum += polygonMoisture[adjacentJ] * 5
			if polygonDepth[adjacentJ] < adjacentMin:
				adjacentMin = polygonDepth[adjacentJ]
				minJ = adjacentJ
		if len(neiList[i]) != 0:
			moistureSum = moistureSum / len(neiList[i])
		if polygonMoisture[i] < moistureSum:
			polygonMoisture[i] = moistureSum
		if adjacentMin <= polygonDepth[i] and minJ != i:
			polygonDepth[i] = adjacentMin + 1
	maxDepth = 0
	for i in range(num_cells):
		if maxDepth < polygonDepth[i]:
			maxDepth = polygonDepth[i]
	for i in range(num_cells):
		polygonDepth[i] = polygonDepth[i] / maxDepth

def getBiomeColor(i):
	if polygonType[i] == 0: # Water
		return (0x44, 0x44, 0x7A)
	elif polygonType[i] == 1: # Coast
		return (0xA0, 0x90, 0x77)
	elif polygonDepth[i] > 0.8:
		if polygonMoisture[i] > 0.5: # Snow
			return (0xFF, 0xFF, 0xFF)
		elif polygonMoisture[i] > 0.33: # Tundra
			return (0xBB, 0xBB, 0xAA)
		elif polygonMoisture[i] > 0.16: # Bare
			return (0x88, 0x88, 0x88)
		else: #Scorched
			return (0x55, 0x55, 0x55)
	elif polygonDepth[i] > 0.6:
		if polygonMoisture[i] > 0.6: # Taiga
			return (0x99, 0xAA, 0x77)
		elif polygonMoisture[i] > 0.33: # Shrubland
			return (0x88, 0x99, 0x77)
		else: # Temperate_desert
			return (0xC9, 0xD2, 0x9B)
	elif polygonDepth[i] > 0.3:
		if polygonMoisture[i] > 0.83: # Temperate Rain Forest
			return (0x44, 0x88, 0x55)
		elif polygonMoisture[i] > 0.50: # Temperate Decidous Forest
			return (0x67, 0x94, 0x59)
		elif polygonMoisture[i] > 0.16: # Grassland
			return (0x88, 0xAA, 0x55)
		else: # Temperate_desert
			return (0xC9, 0xD2, 0x9B)
	else:
		if polygonMoisture[i] > 0.66: # Tropical Rain Forest
			return (0x33, 0x77, 0x55)
		elif polygonMoisture[i] > 0.33: # Tropical Seasonal Forest
			return (0x55, 0x99, 0x44)
		elif polygonMoisture[i] > 0.16: # Grassland
			return (0x88, 0xAA, 0x55)
		else: # Subtropical Desert
			return (0xD2, 0xB9, 0x8B)


def saveImage():
	im = Image.new("RGB", (mapWidth, mapHeight))
	for x in range(mapWidth):
		for y in range(mapHeight):
			im.putpixel((x, y), getBiomeColor(mapMatrix[x][y]))

	im.save("polygon.png", "PNG")

generateVoronoiDiagram()
generatePolygonsMap()
voronoiScipy()
fillPolygonTypes()
saveImage()