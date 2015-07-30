#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import math
from termcolor import colored

import optimization as O
import clustering as Cl

DEFAULT_ERROR = 0.4

class Main():

	global filename
	global data
	global default_error

	def __init__(self, filename, default_error = DEFAULT_ERROR):
		self.filename = filename
		self.data = self.readData()
		self.default_error = default_error

	def computeScores(self, verbose = True, optimize = True, dmax = 0.5):

		score = self.computeProbabilities()
		for d in score:
			o = O.Optimization(self.filterData(d), score[d])
			e = o.getInitialLikelyhood()
			if optimize:
				o.setState(allEquals = True)
				r = o.minimizeLikelyhood()
				e = r['v_f']
				score[d] = r['state_f']
			if verbose:
				print colored("\t---- " + d + " ----", "red"), "(%.2f)" % e
				cl = Cl.Clustering(score[d])
				cl.getClustering(dmax, verror = True)
		return score

	def getSpecificDetails(self, i = 0):
		score = self.computeProbabilities()
		count = 0
		for d in score:
			if count == i:
				return self.filterData(d), score[d]
			count += 1

	def filterData(self, dimension):
		tmp = list()
		for line in self.data:
			if line['dimension'] == dimension:
				tmp.append(line)
		return tmp

	def readData(self):
		f = open(self.filename, 'r')
		data = csv.reader(f, delimiter = ',', quotechar = '"')

		header = data.next()
		if len(set(header)) != 5:
			print colored("\tNão encontrou 5 dimensões!!")
			return 0

		allDilemmas = list()
		row = data.next()
		for i in range(len(row)):
			allDilemmas.append({'name': row[i], 'dimension': header[i], 'dilemma': dict()})

		for row in data:
			for i in range(len(row)):
				if row[i] not in allDilemmas[i]['dilemma']:
					allDilemmas[i]['dilemma'][row[i]] = 1
				else:
					allDilemmas[i]['dilemma'][row[i]] += 1

		return allDilemmas

	def computeProbabilities(self):

		score = dict()
		dim = set(d['dimension'] for d in self.data)

		tmp = dict()

		for d in dim:
			tmp[d] = set()
			for line in self.data:
				if line['dimension'] == d:
					tmp[d] = tmp[d].union(set(line['dilemma'].keys()))

		for d in tmp:
			score[d] = list()
			for b in tmp[d]:
				total = 0
				weight = 0
				for line in self.data:
					if line['dimension'] == d and b in line['dilemma']:
						weight += line['dilemma'][b]
						total += sum(line['dilemma'].values())
				score[d].append({'w': float(weight) / total, 'e': self.default_error, 'name': b})

		return score

	def printDilemmas(self, dimension = None):

		dimensions = set(x['dimension'] for x in self.data)
		n = len(dimensions)
		if dimension == None:
			choice = range(n)
		elif type(dimension) == int:
			choice = [dimension]
		else:
			choice = dimension

		choosen_dimensions = list()
		count = 0
		for d in dimensions:
			if count in choice:
				choosen_dimensions.append(d)
			count += 1

		for d in self.data:
			if d['dimension'] in choosen_dimensions:
				print "\t", colored("Q:   ", "blue"), d['name']
				for item in d['dilemma']:
					print "\t\t", colored(d['dilemma'][item], "green"), "\t", item
				print "\t", colored("Dim: ", "red"), d['dimension']
				print

	def printScores(self, verbose = False, error = False):

		score = self.computeScores(verbose = False, optimize = True)
		for d in score:
			if error:
				quality = self.qualityScore(score[d], d)
			print "\t", colored(d, "yellow")
			for item in score[d]:
				if item['w'] > 0:
					print "\t\t", colored(" %.3f" % item['w'], "green"), 
				else:
					print "\t\t", colored("%.3f" % item['w'], "green"),
				if error:
					print colored(" (%.1f)" % (100 * float(quality[item['name']]['total']) / quality[item['name']]['num']), "red"),
				if verbose:
					print colored(" +- %.3f" % item['e'], "yellow"),
				print "\t", item['name']

	def qualityScore(self, scores, dimension):

		tmp = dict()
		for b in scores:
			tmp[b['name']] = {'w': b['w']}

		for d1 in tmp:
			num = 0
			total = 0
			for datum in self.data:
				if (datum['dimension'] == dimension) and (d1 in datum['dilemma']):
					for d2 in tmp:
						if d2 in datum['dilemma']:
							if tmp[d1]['w'] > tmp[d2]['w']:
								total += (tmp[d1]['w'] - tmp[d2]['w']) * datum['dilemma'][d2]
							else:
								total += (tmp[d2]['w'] - tmp[d1]['w']) * datum['dilemma'][d1]
					num += sum(datum['dilemma'].values())
			tmp[d1]['total'] = total
			tmp[d1]['num'] = num

		return tmp

	def printData(self):

		copy = self.data[:]

		scores = self.computeScores(verbose = False)
		for d in scores:
			score = scores[d]
			print "\t", colored(d, "yellow")
			for datum in copy:
				if datum['dimension'] == d:
					print "\t", colored("Question:  ", "blue"), datum['name']
					for item in datum['dilemma']:
						print "\t\t", colored(datum['dilemma'][item], "green"), "\t", item
					print "\t", colored("Quality:   ", "red"), "%.2f" % (100 * self.qualityDilemma(score, datum)),
					print "\t", colored("Influence:   ", "red"), "%.2f" % (100 * self.influenceDilemma(d, score, datum))
					print

	def qualityDilemma(self, score, dilemma):

		tmp = dict()
		total = 0
		choices = 0
		for s in score:
			if s['name'] in dilemma['dilemma']:
				tmp[s['name']] = {'n': dilemma['dilemma'][s['name']], 'w': s['w']}
				total += dilemma['dilemma'][s['name']]
				choices += 1

		error = 0
		for i in tmp:
			for j in tmp:
				if tmp[i]['w'] < tmp[j]['w']:
					error += (tmp[j]['w'] - tmp[i]['w']) * tmp[i]['n']

		return error / (total * (choices - 1))


	def influenceDilemma(self, dimension, score, dilemma):

		self.data.remove(dilemma)
		tmpScores = self.computeScores(verbose = False)
		tmpScore = tmpScores[dimension]
		self.data.append(dilemma)

		tmp = 0
		for i in score:
			for j in tmpScore:
				if i['name'] == j['name']:
					tmp += (i['w'] - j['w'])**2
		return tmp
