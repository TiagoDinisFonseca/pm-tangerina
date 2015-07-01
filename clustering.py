import math
from termcolor import colored

class Clustering():

	global rated

	def __init__(self, rated):
		self.rated = rated

	def createPockets(self, default_e = 1):
		pockets = list()
		for r in self.rated:
			pockets.append({'w': r['w'], 'e': r['e'], 'elements': [r]})
		return pockets

	def computeDistance(self, pocketA, pocketB):
		return math.sqrt( 2 * (pocketA['w'] - pocketB['w'])**2 / (pocketA['e']**2 + pocketB['e']**2))

	def combinePockets(self, pocketA, pocketB):

		n = len(pocketA['elements']) + len(pocketB['elements'])
		w = sum([r.get('w') for r in pocketA['elements']]) + sum([r.get('w') for r in pocketB['elements']])
		e = sum([r.get('e')**2 for r in pocketA['elements']]) + sum([r.get('e')**2 for r in pocketB['elements']])

		w = float(w) / n
		e = math.sqrt( float(e) / n)

		return {'w': w, 'e': e, 'elements': pocketA['elements'] + pocketB['elements']}

	def findMinDistance(self, pockets):

		n = len(pockets)
		if n < 2:
			return None

		d = self.computeDistance(pockets[0], pockets[1])
		pair = [0, 1]

		for i in range(n):
			for j in range(i+1, n):
				tmp = self.computeDistance(pockets[i], pockets[j])
				if tmp < d:
					d = tmp
					pair = [i, j]

		return pair, d

	def iterate(self, pockets, dmax):

		while(len(pockets) > 1):
			pair, d = self.findMinDistance(pockets)
			if d > dmax:
				break
			pocketA = pockets[pair[0]]
			pocketB = pockets[pair[1]]
			pocket = self.combinePockets(pocketA, pocketB)
			pockets.remove(pocketA)
			pockets.remove(pocketB)
			pockets.append(pocket)

		return pockets

	def getClustering(self, dmax, verbose = True, verror = False):

		pockets = self.createPockets()
		n = len(pockets)
		pockets = self.iterate(pockets, dmax)

		pockets = sorted(pockets, key = lambda k: - k['w'])

		if verbose:
			count = 0
			for pocket in pockets:

				count += 1
				symbolColor = "yellow"
				if count == 1 and len(pocket['elements']) <= math.sqrt(n):
					symbolColor = "green"
				elif count == len(pockets) and len(pocket['elements']) <= math.sqrt(n):
					symbolColor = "red"

				print
				elements = sorted(pocket['elements'], key = lambda k: -k['w'])
				for e in elements:
					print colored("\t\t#", symbolColor),
					if e['w'] > 0:
						print colored(" %.3f" % e['w'], "green"),
					else:
						print colored("%.3f" % e['w'], "green"),
					if verror:
						print colored(" +- %.3f" % e['e'], "yellow"),
					print "\t", e['name']
			print

		return pockets

