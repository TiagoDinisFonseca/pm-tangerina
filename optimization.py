#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import math
from termcolor import colored

import scipy.special as special
from scipy.optimize import minimize

MINIMUM_LOG = -20

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
		r['state_i'] = self.normalizeScores(self.transformXinScores(x))
		r['v_i'] = self.getLikelyhood(x)
		r['dressed_i'] = self.getDressedLikelyhood(x)

		if(verbose):
			print colored("\tInitial: %.1f" % r['v_i'], "red")
			clustering = Cl.Clustering(r['state_i'])
			clustering.getClustering(cl_max, verror = True)

		b = self.getBoundaries()
		# L-BFGS-B, TNC, COBYLA, SLSQP
		result = minimize(self.getDressedLikelyhood, x, bounds = b, method = self.method)

		r['state_f'] = self.normalizeScores(self.transformXinScores(result.x))
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

	def normalizeScores(self, score):
		n = len(score)
		total = sum([k['w'] for k in score])
		for s in score:
			s['w'] -= total / n
		return score
