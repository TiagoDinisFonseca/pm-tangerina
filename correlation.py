#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import csv
from termcolor import colored

class Correlation():

	global url
	global guys
	global header

	def __init__(self, url):
		self.url = url
		self.readFile()

	def readFile(self):

		f = open(self.url, 'r')
		data = csv.reader(f, delimiter = ',', quotechar = '"')

		dimensions = data.next()
		questions = data.next()

		self.header = list()
		for i in range(len(dimensions)):
			self.header.append({'question': questions[i], 'dimension': dimensions[i]})

		self.guys = list()
		for row in data:
			self.guys.append(row)

	def computeCorrelation(self, i, j, ans_i, ans_j):

		both = 0
		num = len(self.guys)
		ai = 0
		aj = 0

		for guy in self.guys:
			if guy[i] == ans_i:
				ai += 1
			if guy[j] == ans_j:
				aj += 1
			if guy[i] == ans_i and guy[j] == ans_j:
				both += 1
		r = float(num * both + num) / float(ai * aj + num)
		return {'both': both, 'seperate_i': ai, 'seperate_j': aj, 'num': num, 'corr': r}
			
	def getBehaviours(self, i):
		b = set()
		for guy in self.guys:
			b.add(guy[i])

		return list(b)

	def computeCorrelations(self):

		results = list()

		for i in range(len(self.header)):
			b_i = self.getBehaviours(i)
			for j in range(i +1, len(self.header)):
				b_j = self.getBehaviours(j)
				for c_i in b_i:
					for c_j in b_j:
						r = self.computeCorrelation(i, j, c_i, c_j)
						r['qi'] = self.header[i]['question']
						r['qj'] = self.header[j]['question']
						r['di'] = self.header[i]['dimension']
						r['dj'] = self.header[j]['dimension']
						r['ci'] = c_i
						r['cj'] = c_j
						results.append(r)
		return sorted(results, key = lambda k: -k['corr'])

	def printCorrelations(self, answersMin = 0, quantity = None, top = True):

		corr = self.computeCorrelations()
		tmp = list()

		for c in corr:
			if c['seperate_i'] > answersMin and c['seperate_j'] > answersMin:
				tmp.append(c)

		if quantity == None:
			for c in tmp:
				self.printCorrelation(c)
		else:
			if top:
				for i in range(quantity):
					self.printCorrelation(tmp[i])
			else:
				for i in range(quantity):
					self.printCorrelation(tmp[len(tmp) - 1 - i])

	def printCorrelation(self, corr):
		
		print "\n\t", colored(corr['di'] + " : " + corr['qi'], "yellow")
		print "\t\t", colored(corr['ci'], "blue")
		print "\t", colored(corr['dj'] + " : " + corr['qj'], "yellow")
		print "\t\t", colored(corr['cj'], "blue")
		print "\t\t\t", colored("%.1f" % (100 * corr['corr']), "red"), "\t\t", str(corr['both']), "  :::  ", str(corr['seperate_i']), " : ", str(corr['seperate_j'])
