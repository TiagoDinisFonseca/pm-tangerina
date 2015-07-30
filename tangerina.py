# coding= utf8
import math
from termcolor import colored
import random
import itertools
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy.special as special
import sys

import optimization as O

class Behaviours():
	
	global behave

	def __init__(self, num = 5):
		self.behave = list()
		self.random(num)

	def create(self, data):
		items = sorted(data, key = lambda x: -x[0]) #sort by the first element
		self.behave = list()
		count = 1
		for item in items:
			behaviour = dict()
			behaviour['name'] = 'B '+str(count)
			behaviour['weight'] = item[0]
			behaviour['error'] = item[1]
			count += 1
			self.behave.append(behaviour)
		return
		
	def random(self, n, min_error = 1, max_error = 3):
		tmp = list()
		for i in range(n):
			tmp.append([random.uniform(0, 10), random.uniform(min_error, max_error)])
		self.create(tmp)	
		return

	def printBehaviours(self, normalized = False):
		if normalized:
			average = sum([behaviour['weight'] for behaviour in self.behave]) / len(self.behave)
			tmp = list()
			for behaviour in self.behave:
				print colored("\tname:", "blue"), behaviour['name'], colored("\tweight:", "blue"), "%.3f" % ((behaviour['weight'] - average) / 10), colored("\terror:", "blue"), "%.3f" % (behaviour['error'] / 10)
		else:
			for behaviour in self.behave:
				print colored("\tname:", "blue"), behaviour['name'], colored("\tweight:", "blue"), round(behaviour['weight'], 1), colored("\terror:", "blue"), round(behaviour['error'], 1)

	def number(self):
		return len(self.behave)

	def names(self):
		names = list()
		for behaviour in self.behave:
			names.append(behaviour['name'])
		return names

	def behaviours(self):
		tmp = list()
		for behaviour in self.behave:
			tmp.append((behaviour['weight'], behaviour['error']))
		return tmp

	def getAnswers(self, query):

		answers = dict()

		for q in query:
			behaviour = None
			for b in self.behave:
				if b['name'] == q:
					behaviour = b
			if behaviour == None:
				answers[q] = 0
			else:
				answers[q] = random.gauss(behaviour['weight'], behaviour['error'])

		return answers

	def getClassification(self):

		classification = dict()
		for b in self.behave:
			classification[b['name']] = b['weight']
		return classification
		
	def getNormalizedBehaviours(self):

		nb = list()
		maximum = max([i.get('weight') for i in self.behave])
		minimum = min([i.get('weight') for i in self.behave])

		for i in self.behave:
			nb.append([(i['weight'] - minimum) / (maximum - minimum), i['error'] / (maximum - minimum)])
		return nb

	def makeGraph(self, error = 3):

		X = np.arange(-2*error, 10+2*error, 0.01)
		for b in self.behave:
			Y = mlab.normpdf(X, b['weight'], b['error'])
			plt.plot(X, Y)
		
		return plt

class Dilemmas():

	global dilemmas
	global behaviours
	global solutions
	global classification

	def __init__(self, behaviours):
		self.dilemmas = list()
		self.solutions = list()
		self.classification = dict()
		self.behaviours = behaviours
		self.createWithPairs()

	def createWithPairs(self, numberSolutions = 3):
		
		b = self.behaviours.names()
		random.shuffle(b)

		all_dilemmas = list()
		for example in itertools.combinations(b, numberSolutions):
			pairs = list()
			for pair in itertools.combinations(example, 2):
				pairs.append(pair)
			all_dilemmas.append({'dilemma': example, 'pairs': pairs})
		
		random.shuffle(all_dilemmas)
		self.dilemmas = list()
		name = 1

		notFinish = True
		while notFinish:

			n = 0
			choosen = None
			for dilemma in all_dilemmas:
				if(len(dilemma['pairs']) > n):
					choosen = dilemma
					n = len(dilemma['pairs'])

			if n == 0:
				notFinish = False
				break

			all_dilemmas.remove(choosen)

			particular = dict()
			particular['dilemma'] = choosen['dilemma']
			particular['name'] = "D " + str(name)
			name += 1
			
			self.dilemmas.append(particular)

			for dilemma in all_dilemmas:
				for pair in choosen['pairs']:
					if pair in dilemma['pairs']:
						dilemma['pairs'].remove(pair)

	def createRandom(self, numberSolutions = 3, repetitions = 3, minimum = True):
		
		self.dilemmas = list()

		dilemmas = list()
		extra = set()

		for r in range(repetitions):

			B = set(self.behaviours.names())
			choice = set()

			if len(extra) > 0:
				choice = extra.copy()
				extra.clear()

			while len(B) >= numberSolutions:
				while len(choice) < numberSolutions:
					item = random.choice(list(B - choice))
					choice.add(item)
					B.remove(item)
				dilemmas.append(tuple(sorted(choice)))
				choice.clear()

			extra = B.copy()
			B.clear()

		B = set(self.behaviours.names())
		if minimum and len(extra) > 0:
			choice = extra.copy()
			while len(choice) < numberSolutions:
				item = random.choice(list(B - choice))
				choice.add(item)
				B.remove(item)
			dilemmas.append(tuple(sorted(choice)))

		tmp = 1
		for dilemma in dilemmas:
			self.dilemmas.append({'dilemma': dilemma, 'name': 'D ' + str(tmp)})
			tmp += 1

	def printDilemmas(self):
		for dilemma in self.dilemmas:
			print colored("\tDilemma: ", "blue"), dilemma["name"], colored("\tAnswers: ", "blue"), ", ".join(dilemma['dilemma'])

	def number(self):
		return len(self.dilemmas)

	def countBehaviours(self):
		count = dict()
		for b in self.behaviours.names():
			count[b] = 0

		for d in self.dilemmas:
			for b in d['dilemma']:
				count[b] += 1

		for b in count:
			print colored("\t" + b + ":\t", "blue"), "*" * count[b]

	def chooseAnswers(self, repeat = 100):

		results = dict()
		for r in range(repeat):
			d = random.choice(self.dilemmas)
			if d['name'] not in results:
				results[d['name']] = dict()
				for b in d['dilemma']:
					results[d['name']][b] = 0
			answers = self.behaviours.getAnswers(d['dilemma'])
			choosen = max(answers, key = answers.get)
			results[d['name']][choosen] += 1

		self.solutions = list()
		for d in results:
			self.solutions.append({'dilemma': d, 'result': results[d]})

	def printBehaviours(self):
		self.behaviours.printBehaviours()

	def printSolutions(self):
		for dilemma in self.dilemmas:
			solution = None
			for s in self.solutions:
				if s['dilemma'] == dilemma['name']:
					solution = s
			print colored("\t--- Dilemma: ", "red") + dilemma['name'] + colored("\tAnswers: ", "red") + ", ".join(dilemma['dilemma']) + colored("\t---", "red")
			for s_item in sorted(solution['result']): 
				print colored("\t" + s_item + ": ", "green") + str(solution['result'][s_item])  

	def printCrossSolutionTable(self, table):

		B = self.behaviours.names()
		print "\t",
		for b_y in B:
			print colored("\t" + b_y, "green"),
		
		for b_x in B:
			print colored("\n\t" + b_x, "green"),
			for b_y in B:
				print "\t " + str(round(table[b_x][b_y], 2)),

		print "\n"

	def createCrossSolutionTable(self):
		B = self.behaviours.names()
		table = dict()
		for b_x in B:
			table[b_x] = dict()
			for b_y in B:
				table[b_x][b_y] = 0
				for s in self.solutions:
					if (b_x in s['result']) and (b_y in s['result']) and (b_x != b_y):
						table[b_x][b_y] += s['result'][b_x]
		return table

	def quantifyCrossSolutionTable(self, table):
		B = self.behaviours.names()
		result = dict()
		for b_x in B:
			result[b_x] = dict()
			for b_y in B:
				if (b_x == b_y) or ((table[b_x][b_y] + table[b_y][b_x]) <= 0):
					result[b_x][b_y] = 0
				else:
					result[b_x][b_y] = float((table[b_x][b_y] - table[b_y][b_x])) / (table[b_x][b_y] + table[b_y][b_x])
		return result

	def classifyCrossTableSimple(self, verbose=False):
		table = self.createCrossSolutionTable()
		if verbose:
			print colored("\t\t--- Cross solution table ---", "red")
			self.printCrossSolutionTable(table)

		table = self.quantifyCrossSolutionTable(table)
		if verbose:
			print colored("\t\t--- Relative solution table ---", "red")
			self.printCrossSolutionTable(table)
				
		B = self.behaviours.names()
		result = dict()
		for b in B:
			tmp = 0
			for b_extra in B:
				if b != b_extra:
					tmp += table[b][b_extra]
			tmp = tmp / (len(B) - 1)
			result[b] = tmp

		for b in result:
			result[b] = (1 + result[b]) / 2
		self.classification = Classification(self.behaviours, result)
		return self.classification

	def classifyCounting(self):
		B = self.behaviours.names()
		result = dict()
		for b in B:
			n_choosen = 0
			n_total = 0
			for s in self.solutions:
				if b in s['result']:
					n_total += sum(s['result'].values())
					n_choosen += s['result'][b]
			if n_total != 0:
				result[b] = float(n_choosen) / n_total

		self.classification = Classification(self.behaviours, result)
		return self.classification

	def permutationsFailureRate(self, b, table):
		
		pairs = itertools.combinations(b, 2)

		tmp = 0.0
		for pair in pairs:
			bad = table[pair[1]][pair[0]]
			good = table[pair[0]][pair[1]]
			if bad > good:
				tmp += float(bad-good) / (bad+good)
		return tmp

	def orderByAllPossibilities(self):

		table = self.createCrossSolutionTable()

		B = self.behaviours.names()
		permutations = dict()
		permB = itertools.permutations(B)

		for b in permB:
			permutations[b] = self.permutationsFailureRate(b, table)

		return min(permutations, key = permutations.get)

	def classifyRandom(self):
		B = self.behaviours.names()
		result = dict()
		for b in B:
			result[b] = random.uniform(0, 10)
		self.classification = Classification(self.behaviours, result)
		return self.classification
	
	def prepareOptimization(self):
		tmp = self.classifyCounting()
		score = list()
		answers = list()
		for u in tmp.classification:
			score.append({'e': 0.3, 'w': u['value'], 'name': u['behaviour']})
		for s in self.solutions:
			answers.append({'dimension': 'Unique', 'name': s['dilemma'], 'dilemma': s['result']})
		return score, answers

	def classifyOptimization(self, allEquals = True):	
		score, answers = self.prepareOptimization()
		o = O.Optimization(answers, score)
		o.setState(allEquals = allEquals)
		r = o.minimizeLikelyhood()
		result = dict()
		for i in r['state_f']:
			result[i['name']] = i['w']
		self.classification = Classification(self.behaviours, result)
		return self.classification

class Classification(dict):

	global classification
	global ordering
	global behaviours

	def __init__(self, behaviours, classification):
		self.classification = list()
		c = self.normalize(classification)
		self.ordering = list()
		for b in sorted(c, key=c.get, reverse=True):
			self.classification.append({"behaviour": b, "value": c[b]})
			self.ordering.append(b)
		self.behaviours = behaviours

	def normalize(self, classification):
		c_max = max(classification.values())
		c_min = min(classification.values())
		c = dict()
		if c_max > c_min:
			for d in classification:
				c[d] = (classification[d] - c_min) / (c_max - c_min)
		else:
			for d in classification:
				c[d] = 0.5
		return c

	def printClassification(self):
		for c in self.classification:
  			print colored("\t" + c["behaviour"] + "\t", "green"), round(c["value"], 3)

	def computeError(self):
		real = self.behaviours.getClassification()

		error = 0
		for c1 in self.classification:
			for c2 in self.classification:
				tmp = (real[c1['behaviour']] - real[c2['behaviour']]) * (c1['value'] - c2['value']) * (real[c1['behaviour']] + real[c2['behaviour']])
				if tmp < 0:
					error -= tmp
		
		return math.pow(error, 2./3)

class Simulation():

	global results

	global nRuns
	global nRepetitions
	global nBehaviours
	global verbose
	global nAnswers

	def __init__(self, nBehaviours = 5, nRuns = 10, nRepetitions = 100, nAnswers = 20, verbose=False):
		self.nBehaviours = nBehaviours
		self.nRepetitions = nRepetitions
		self.nRuns = nRuns
		self.verbose = verbose
		self.nAnswers = nAnswers

	def simulateSimple(self, definitions):

		self.results = list()

		b = Behaviours()
		b.random(self.nBehaviours)
		if self.verbose:
			b.printBehaviours

		for definition in definitions:
			definition['dilemmas']['object'] = Dilemmas(b)
			if definition['dilemmas']['method'] == 'pairs':
				if 'nSolutions' in definition['dilemmas']:
					nS = definition['dilemmas']['nSolutions']
				else:
					nS = 3

				definition['dilemmas']['object'].createWithPairs(numberSolutions = nS)

			elif definition['dilemmas']['method'] == 'balanced':
				if 'nSolutions' in definition['dilemmas']:
					nS = definition['dilemmas']['nSolutions']
				else:
					nS = 3

				if 'repetitions' in definition['dilemmas']:
					r = definition['dilemmas']['repetitions']
				else:
					r = 3

				definition['dilemmas']['object'].createRandom(numberSolutions = nS, repetitions = r)

		result = list()
		for i in range(self.nRuns):

			resultLine = dict()
			
			for definition in definitions:
				d = definition['dilemmas']['object']
				d.chooseAnswers(self.nAnswers)
				if definition['classification']['method'] == 'counting':
					resultLine[definition['name']] = d.classifyCounting().computeError()
				elif definition['classification']['method'] == 'crossTable':
					resultLine[definition['name']] = d.classifyCrossTableSimple().computeError()
				elif definition['classification']['method'] == 'optimization':
					resultLine[definition['name']] = d.classifyOptimization(allEquals = True).computeError()
				elif definition['classification']['method'] == 'optimizationEqual':
					resultLine[definition['name']] = d.classifyOptimization(allEquals = True).computeError()
				elif definition['classification']['method'] == 'optimizationFree':
					resultLine[definition['name']] = d.classifyOptimization(allEquals = False).computeError()
				elif definition['classification']['method'] == 'random':
					resultLine[definition['name']] = d.classifyRandom().computeError()
			result.append(resultLine)

		return result	

	def simulateRepeated(self, definitions):
		data = list()
		for i in range(self.nRepetitions):
			data.extend(self.simulateSimple(definitions))
		return data

	def simulationSummary(self, definitions):
		result = dict()
		data = self.simulateRepeated(definitions)
		for definition in definitions:
			result[definition['name']] = dict()
			mean = self.getMean(data, definition['name'])
			sd = self.getSD(data, definition['name'], mean)
			result[definition['name']]['mean'] = mean
			result[definition['name']]['sd'] = sd 
		return result

	def getMean(self, data, name):
		tmp = 0.0
		n = 0
		for d in data:
			tmp += d[name]
			n += 1
		if n > 0:
			return float(tmp) / n
		else:
			return 0

	def getSD(self, data, name, mean):
		tmp = 0.0
		n = 0
		for d in data:
			tmp += (d[name] - mean) ** 2
			n += 1
		if n > 0:
			return math.sqrt(float(tmp) / n)
		else:
			return 0

	def simulationByNumberAnswers(self, definitions, maxAnswers = 1000, step = 10):

		results = list()
		for i in range(step, maxAnswers + 1 , step):
			if self.verbose:
				print "\t", colored(str(i), "green")
			else:
				print colored(":", "yellow"),
				sys.stdout.flush()
			self.nAnswers = i
			result = self.simulationSummary(definitions)
			results.append({'x': i, 'result': result})
		
		return results

	def defaultDefinitions(self, nSolutions = 3):

		definitions = list()

		# pairs - counting
		definition = dict()
		definition['name']	= 'counting'
		definition['dilemmas'] = {'method': 'pairs', 'nSolutions': nSolutions}
		definition['classification'] = {'method': 'counting'}
		definition['visible'] = True
		definitions.append(definition)

		# pairs - optimization - equal sd
		definition = dict()
		definition['name']	= 'optimizationEqual'
		definition['dilemmas'] = {'method': 'pairs', 'nSolutions': nSolutions}
		definition['classification'] = {'method': 'optimizationEqual'}
		definition['visible'] = True
		definitions.append(definition)

		# pairs - optimization - free sd
		definition = dict()
		definition['name']	= 'optimizationFree'
		definition['dilemmas'] = {'method': 'pairs', 'nSolutions': nSolutions}
		definition['classification'] = {'method': 'optimizationFree'}
		definition['visible'] = True
		definitions.append(definition)

		# random
		definition = dict()
		definition['name']	= 'random'
		definition['dilemmas'] = {'method': 'pairs', 'nSolutions': nSolutions}
		definition['classification'] = {'method': 'random'}
		definition['visible'] = False
		definitions.append(definition)
	
		return definitions

	def defaultDefinitionsPairsBalanced(self, nSolutions = 3, repetitions = range(3, 5)):

		definitions = list()

		# pairs
		definition = dict()
		definition['name']	= 'pairs'
		definition['dilemmas'] = {'method': 'pairs', 'nSolutions': nSolutions}
		definition['classification'] = {'method': 'counting'}
		definition['visible'] = True
		definitions.append(definition)

		# balanced
		for r in repetitions:
			definition = dict()
			definition['name']	= 'balance.' + str(r)
			definition['dilemmas'] = {'method': 'balanced', 'nSolutions': nSolutions, 'repetitions': r}
			definition['classification'] = {'method': 'counting'}
			definition['visible'] = True
			definitions.append(definition)

		# random
		definition = dict()
		definition['name']	= 'random'
		definition['dilemmas'] = {'method': 'pairs', 'nSolutions': nSolutions}
		definition['classification'] = {'method': 'random'}
		definition['visible'] = False
		definitions.append(definition)
	
		return definitions

	def makeGraphByNumberAnswers(self, definitions = None, maxAnswers = 100, step = 5):

		m = 1. / math.sqrt(self.nRepetitions)

		if definitions == None:
			definitions = self.defaultDefinitions()
		results = self.simulationByNumberAnswers(definitions, maxAnswers = maxAnswers, step = step)

		graph = dict()
		graph['x'] = list()
		graph['y'] = dict()
		graph['sd'] = dict()
		for d in definitions:
			if d['visible']:
				graph['y'][d['name']] = list()
				graph['sd'][d['name']] = list()

		for r in results:
			graph['x'].append(r['x'])
			for name in graph['y']:
				graph['y'][name].append(r['result'][name]['mean']/r['result']['random']['mean'] )
				graph['sd'][name].append(m * r['result'][name]['sd']/r['result']['random']['mean'])

		for name in graph['y']:
			plt.errorbar(graph['x'], graph['y'][name], graph['sd'][name], marker = 'o', ls = 'dotted', label = name)

		plt.legend()
		return plt

	def getMinimumNumberAnswers(self, mins, definitions = None):

		if definitions == None:
			definitions = self.defaultDefinitions(nSolutions = 3)
		results = self.simulationByNumberAnswers(definitions, maxAnswers = 300, step = 5)
		results.reverse()

		final = dict()
		
		for d in definitions:
			if d['visible']:
				final[d['name']] = dict()

		for m in mins:
			for r in results:
				for name in final:
					if m > r['result'][name]['mean'] / r['result']['random']['mean']:
						final[name][str(m)] = r['x']

		return final

	def printMinimumNumberAnswers(self, definition, result):

		print
		for d in definition:
			print colored("\t" + d + ": ", "red"), definition[d],
		for r in result:
			print colored("\t" + r + ": ", "blue"),
			for i in sorted(result[r]):
				print colored("\t" + i + ": ", "green"), result[r][i],
		print

	def getMinimumNumberAnswersByParameters(self, mins, nBehaviours, nSolutions):

		results = list()
		for nS in nSolutions:
			definitions = self.defaultDefinitions(nS)
			for nB in nBehaviours:
				if nB >= nS:
					self.nBehaviours = nB
					result = self.getMinimumNumberAnswers(mins)
					definitions = {'nS': nS, 'nB': nB}
					self.printMinimumNumberAnswers(definitions, result)
					results.append({'nBehaviours': nB, 'nSolutions': nS, 'Minimum': result})

		return results

	def getPrintResultsMinimumNumberAnswersByParameters(self, lines, mins):

		print colored("\tnS\tnB:", "red"),
		for method in sorted(lines[0]['Minimum']):
			print colored("\t" + method + ((2*len(mins) - 2)*"\t"), "blue"),
		print

		for line in lines:
			print "\t", line['nSolutions'], "\t", line['nBehaviours'],
			for method in sorted(line['Minimum']):
				for i in sorted(mins, reverse=True):
					if str(i) in line['Minimum'][method]:
						tmp = str(line['Minimum'][method][str(i)])
					else:
						tmp = '--'
					print colored("\t" + str(i) + " -", "green"), tmp,
			print

class Counting():

	def countDilemmasPairs(self, n, k):

		if k > n:
			return '-'
		b = Behaviours()
		b.random(n)
		d = Dilemmas(b)
		d.createWithPairs(numberSolutions = k)
		return str(d.number())

	def printTablePairs(self, n_vector = range(3, 16), k_vector = (3, 4, 5)):

		print colored("\tn\k", "red"), 
		for k in sorted(k_vector):
			print colored("\t" + str(k), "green"),
		for n in sorted(n_vector):
			print colored("\n\t" + str(n), "green"), 
			for k in sorted(k_vector):
				print "\t" + self.countDilemmasPairs(n, k), 

	def countDilemmasRepetitions(self, n, k, r):
		a = n*r
		if a % k == 0:
			return str(a/k)
		else:
			return str(a/k + 1)


	def printTableRepetitionsVaryingK(self, n_vector = range(3, 16), k_vector = (3, 4, 5), r = 3):

		print colored("\tn\k", "red"), 
		for k in sorted(k_vector):
			print colored("\t" + str(k), "green"),
		for n in sorted(n_vector):
			print colored("\n\t" + str(n), "green"), 
			for k in sorted(k_vector):
				print "\t" + self.countDilemmasRepetitions(n, k, r), 

	def printTableRepetitionsVaryingR(self, n_vector = range(3, 16), k=3, r_vector = (3, 4, 5)):

		print colored("\tn\\r", "red"), 
		for r in sorted(r_vector):
			print colored("\t" + str(r), "green"),
		for n in sorted(n_vector):
			print colored("\n\t" + str(n), "green"), 
			for r in sorted(r_vector):
				print "\t" + self.countDilemmasRepetitions(n, k, r), 

