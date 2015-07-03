#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import csv
from termcolor import colored

class Cluster():

	global url
	global guys

	def __init__(self, url, method = 'avg'):
		self.url = url
		if method == 'avg' or method == 'max':
			self.method = method
		else: 
			print colored("\tERROR, unknown method " + method + ". Please choose 'avg' or 'max'", "red")
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
		if self.method == 'avg':
			for x in X:
				for y in Y:
					dist += self.distance(x, y)
			return float(dist) / (nx * ny)
		elif self.method == 'max':
			for x in X:
				for y in Y:
					dist = max(dist, self.distance(x, y))
			return dist

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
			print "\n\t\t", colored("-----  %d guys  -----" % len(p), "red")
			self.showPockets(p)

		print colored("\n\t\t:::::  %d pockets  :::::"%len(pockets), "green"),
		return pockets

	def showPockets(self, pocket):

		for i in range(len(pocket[0])):
			show = True
			name = pocket[0][i]
			for p in pocket:
				if p[i] != name:
					show = False
			if show:
				print colored("\t%d\t"%i, "blue"), name
#			else:
#				print colored("\t%d\t"%i, "blue"), "--"
				
