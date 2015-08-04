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
	global categories

	def __init__(self, filename, default_error = DEFAULT_ERROR, compare = None):
		self.filename = filename
		self.data, self.categories = self.readData(compare)
		self.default_error = default_error

	def computeScoresWithFilter(self, verbose = True, optimize = True, dmax = 0.5):

		filtro = self.getFilterCategories()
		self.applyFilter(filtro)
		self.computeScores(verbose, optimize, dmax)
		self.cleanDataFromFilters()

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

	def getFilterCategories(self):
		print '\t', colored("Qual categorização queres?", 'blue')
		tmp = 0
		for entry in self.categories:
			print '\t\t', colored('[' + str(tmp) + '] ', 'red'), colored(entry['name'], 'yellow')
			tmp += 1
		choice = input('\tEscolha:')
		tmp = set()
		for possibility in self.categories[choice]['key']:
			tmp = tmp.union(possibility)
		i = 0
		tmp = list(tmp)
		print '\t', colored("Qual categoria queres?", 'blue')
		for p in tmp:
			print '\t\t', colored('[' + str(i) + '] ', 'red'), colored(p, 'yellow')
			i += 1
		choice2 = tmp[input('\tEscolha:')]
		i = 0
		results = list()
		for ex in self.categories[choice]['key']:
			if choice2 in ex:
				results.append(i)
			i += 1
		return results

	def cleanDataFromFilters(self):
		for dilemma in self.data:
			for answer in dilemma['dilemma']:
				count = 0
				for k in dilemma['key']:
					if k == answer:
						count += 1
				dilemma['dilemma'][answer] = count

	def applyFilter(self, filtro):
		for dilemma in self.data:
			for answer in dilemma['dilemma']:
				count = 0
				for i in filtro:
					if dilemma['key'][i] == answer:
						count += 1
				dilemma['dilemma'][answer] = count

	def filterData(self, dimension):
		tmp = list()
		for line in self.data:
			if line['dimension'] == dimension:
				tmp.append(line)
		return tmp

	def readData(self, compare = None):
		f = open(self.filename, 'r')
		data = csv.reader(f, delimiter = ',', quotechar = '"')

		header = data.next()
		fields_number = list()
		i = 0
		while 'None' in header:
			tmp_number = header.index('None')
			fields_number.append(tmp_number + i)
			header.pop(tmp_number)
			i += 1

		if len(set(header)) != 5:
			print colored("\tNão encontrou 5 dimensões!!")
			return 0

		allDilemmas = list()
		allCategories = dict()
		row = data.next()
		for i in range(len(row)):
			if i in fields_number:
				allCategories[str(i)] = {'name': row[i], 'key': list()}
			else:
				allDilemmas.append({'name': row[i], 'dimension': header[i], 'dilemma': dict(), 'key': list()})

		for row in data:
			for i in range(len(row)):
				if i in fields_number:
					allCategories[str(i)]['key'].append(self.splitCategories(row[i]))
				else:
					allDilemmas[i]['key'].append(row[i])
					if row[i] not in allDilemmas[i]['dilemma']:
						allDilemmas[i]['dilemma'][row[i]] = 1
					else:
						allDilemmas[i]['dilemma'][row[i]] += 1

		self.comparing(allDilemmas, compare)
		allCategories = allCategories.values()

		return allDilemmas, allCategories

	def splitCategories(self, frase):
		tmp = frase.split('#')
		while '' in tmp:
			tmp.remove('')
		return tmp

	def comparing(self, dilemmas, compare):
		if compare == None:
			for dilemma in dilemmas:
				if len(dilemma['dilemma']) != 3:
					print dilemma['name']
					print dilemma['dimension']
					for d in dilemma['dilemma']:
						print "\t", d
		else:
			for dilemma in dilemmas:
				if len(dilemma['dilemma']) < 3:
					example = None
					for c in compare:
						if c['name'] == dilemma['name']:
							example = c
					for d in example['dilemma']:
						if d not in dilemma['dilemma']:
							dilemma['dilemma'][d] = 0

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
