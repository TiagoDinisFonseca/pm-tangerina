#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import csv

class cluster():

	global url
	global guys

	def __init__(self, url):
		self.url = url
		self.readFile()

	def readFile(self):

		f = open(self.url, 'r')
		data = csv.reader(f, delimiter = ',', quotechar = '"')

		lixo = data.next()
		lixo = data.next()

		self.guys = list()
		for row in data:
			self.guys.append(row)

	def distance(self, x, y):

		tmp = 0
		for i in range(len(x)):
			if x[i] != y[i]:
				tmp += 1

		return tmp

	def distanceGroup(self, X, Y):

		nx = len(X)
		ny = len(Y)

		dist = 0
		for x in X:
			for y in Y:
				dist += self.distance(x, y)

		return float(dist) / (nx * ny)

	def createPockets(self):

		pockets = list()

		for guy in self.guys:
			pockets.append([guy])

		return pockets

	def iterate(self, dmax):

		pockets = self.createPockets()

		while len(pockets) > 1:
			X = pockets[0]
			Y = pockets[1]
			dmin = self.distanceGroup(X, Y)
			for i in range(len(pockets)):
				for j in range(i + 1, len(pockets)):
					if self.distanceGroup(pockets[i], pockets[j]) < dmin:
						dmin = self.distanceGroup(pockets[i], pockets[j])
						X = pockets[i]
						Y = pockets[j]
			if dmin <= dmax:
				pockets.remove(Y)
				X.extend(Y)
			else:
				break

		for p in pockets:
			self.showPockets(p)
		return pockets

	def showPockets(self, pocket):

		for i in range(len(pocket[0])):
			print pocket[0]
			show = True
			name = pocket[0][i]
			for p in pocket:
				if p[i] != name:
					show = False
			if show:
				print colored("\t%d\t"%i, "blue"), name
			else:
				print colored("\t%d\t"%i, "blue"), "--"
				
