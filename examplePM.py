#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import math
from termcolor import colored
import scipy.special as special
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize

import clustering as Cl

DEFAULT_ERROR = 0.4
MINIMUM_LOG = -20

class Main():

	global filename
	global data
	global default_error

	def __init__(self, filename, default_error = DEFAULT_ERROR):
		self.filename = filename
		self.data = self.readData()
		self.default_error = default_error

	def computeScores(self, verbose = True, optimize = True):

		dmax = 1 / (5 * self.default_error)

		score = self.computeProbabilities()
		for d in score:
			o = Optimization(self.filterData(d), score[d])
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

	def printScores(self, verbose = False):

		score = self.computeScores(verbose = False, optimize = True)
		for d in score:
			print "\t", colored(d, "yellow")
			for item in score[d]:
				if item['w'] > 0:
					print "\t\t", colored(" %.3f" % item['w'], "green"), 
				else:
					print "\t\t", colored("%.3f" % item['w'], "green"),
				if verbose:
					print colored(" +- %.3f" % item['e'], "yellow"),
				print "\t", item['name']

	def qualityScore(self, scores, dimension):

		tmp = dict()
		for b in scores:
			tmp[b['name']] = {'w': b['w']}

		print tmp

		for d1 in tmp:
			num = 0
			total = 0
			for datum in self.data:
				if (datum['dimension'] == dimension) and (d1 in datum['dilemma']):
					for d2 in tmp:
						if d2 in datum['dilemma']:
							if tmp[d1]['w'] > tmp[d2]['w']:
								total += (tmp[d1]['w'] - tmp[d2]['w']) * datum['dimension'][d2]
							else:
								total += (tmp[d2]['w'] - tmp[d1]['w']) * datum['dimension'][d1]
					num += sum(datum['dilemma'].values())
			tmp[b]['total'] = total
			tmp[b]['num'] = num

		return tmp

	def printData(self):

		scores = self.computeScores(verbose = False)
		for d in scores:
			score = scores[d]
			print "\t", colored(d, "yellow")
			for datum in self.data:
				if datum['dimension'] == d:
					print "\t", colored("Question:  ", "blue"), datum['name']
					for item in datum['dilemma']:
						print "\t\t", colored(datum['dilemma'][item], "green"), "\t", item
					print "\t", colored("Quality:   ", "red"), "%.1f" % (100 * self.qualityDilemma(score, datum))
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

class Optimization():

	global answers
	global grades
	global names
	global alpha
	global allEquals
	global method

	def __init__(self, answers, scores):
		self.answers = answers
		self.transformScores(scores)
		self.writeBehaviours(scores)
		self.alpha = 0
		self.allEquals = False
		self.method = 'L-BFGS-B'

	def setState(self, method = 'L-BFGS-B', allEquals = False, alpha = 0):
		self.method = method
		self.allEquals = allEquals
		self.alpha = alpha

	def getInitialLikelyhood(self):
		x = self.getInitialState()
		return self.getLikelyhood(x)

	def writeBehaviours(self, scores):
		self.names = list()
		for d in scores:
			self.names.append(d['name'])

	def transformScores(self, scores):
		self.grades = dict()
		for score in scores:
			self.grades[score['name']] = {'w': score['w'], 'e': score['e']}

	def getInitialState(self):
		first = self.names[0]

		x = list()
		if self.allEquals:
			x.append(self.grades[first]['e'])

		for name in self.names:
			if name != first:
				x.append(self.grades[name]['w'] - self.grades[first]['w'])
				if not self.allEquals:
					x.append(self.grades[name]['e'])
		return x

	def transformXinGrades(self, x):

		first = self.names[0]
		grades = dict()

		if self.allEquals:
			grades[first] = {'w': self.grades[first]['w'], 'e': x[0]}
			position = 1
		else:
			grades[first] = {'w': self.grades[first]['w'], 'e': self.grades[first]['e']}
			position = 0
		
		for name in self.names:
			if name != first:
				if self.allEquals:
					grades[name] = {'w': x[position] + self.grades[first]['w'], 'e': x[0]}
					position += 1
				else:
					grades[name] = {'w': x[position] + self.grades[first]['w'], 'e': x[position + 1]}
					position += 2

		return grades

	def transformXinScores(self, x):

		grades = self.transformXinGrades(x)
		scores = list()
		for d in grades:
			scores.append({'name': d, 'w': grades[d]['w'], 'e': grades[d]['e']})
		return scores

	def getBoundaries(self):

		n = len(self.names)
		b = list()

		if self.allEquals:
			b.append((0.2, 0.8))
		for i in range(n-1):
			b.append((-1, 1))
			if not self.allEquals:
				b.append((0.2, 0.8))

		return b

	def dressing(self, x):

		tmp = self.transformXinGrades(x)
		diff = 0
		count = 0
		for i in tmp:
			for j in tmp:
				if i != j:
					count += 1
					diff += (tmp[i]['e'] - tmp[j]['e'])**2

		return self.alpha * diff

	def minimizeLikelyhood(self, verbose = False, cl_max = 0.5):

		r = dict()
		x = self.getInitialState()
		r['state_i'] = self.transformXinScores(x)
		r['v_i'] = self.getLikelyhood(x)
		r['dressed_i'] = self.getDressedLikelyhood(x)

		if(verbose):
			print colored("\tInitial: %.1f" % r['v_i'], "red")
			clustering = Cl.Clustering(r['state_i'])
			clustering.getClustering(cl_max, verror = True)

		b = self.getBoundaries()
		# L-BFGS-B, TNC, COBYLA, SLSQP
		result = minimize(self.getDressedLikelyhood, x, bounds = b, method = self.method)

		r['state_f'] = self.transformXinScores(result.x)
		r['v_f'] = self.getLikelyhood(result.x)
		r['dressed_f'] = self.getDressedLikelyhood(result.x)

		if verbose:
			print colored("\tFinal: %.1f" % result.fun, "red")
			clustering = Cl.Clustering(self.transformXinScores(result.x))
			clustering.getClustering(cl_max, verror = True)

		return r

	def getDressedLikelyhood(self, x):
		return self.dressing(x) + self.getLikelyhood(x)

	def getLikelyhood(self, x):

		tmp = self.transformXinGrades(x)

		likelyhood = 0
		for dilemma in self.answers:
			likelyhood -= self.getIndividualLikelyHood(dilemma['dilemma'], tmp)

		return likelyhood

	def getIndividualLikelyHood(self, dilemma, tmp):

		prob = dict()
		for b in dilemma:
			partial = 1
			for x in dilemma:
				if x != b:
					partial *= self.probabilityOneAgainstOne(tmp[b]['w'] - tmp[x]['w'], tmp[b]['e']**2 + tmp[x]['e']**2)
			prob[b] = partial

		total = sum(prob.values())
		for p in prob:
			prob[p] = prob[p] / total

		tmp = self.getLikelyhoodFromProbabilities(dilemma, prob)
		if tmp <= 0:
			return MINIMUM_LOG
		else:
			return math.log(tmp)

	def getLikelyhoodFromProbabilities(self, dilemma, prob):

		n = sum(dilemma.values())
		product = math.factorial(n)
		for b in prob:
			if b in dilemma:
				product *= math.pow(prob[b], dilemma[b])
		for b in dilemma:
			product *= float(1) / math.factorial(dilemma[b])
		return product

	def probabilityOneAgainstOne(self, difference, variance):
		return 0.5 + 0.5 * special.erf(difference / math.sqrt(2 * variance))
