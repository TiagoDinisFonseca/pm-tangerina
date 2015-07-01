import math
import random
from termcolor import colored

nGrade = 3
nBehaviours = 5
hole = 0.05
replace = True
nGuys = 50
minVote = 1
maxVote = 6
meanVote = 3.5 # (minVote + maxVote)/2

manual = [{'cl': 3, '-': 0, '0': 0, '+': 3}, {'cl': 2.1, '-': 0, '0': 1, '+': 2}, {'cl': 2, '-': 0, '0': 0, '+': 2}, {'cl': 1.2, '-': 0, '0': 2, '+': 1}, {'cl': 1.1, '-': 0, '0': 1, '+': 1}, {'cl': 1, '-': 0, '0': 0, '+': 1}, {'cl': 0.0, '-': 1, '0': 0, '+': 2}, {'cl': 0.3, '-': 0, '0': 3, '+': 0}, {'cl': 0.2, '-': 0, '0': 2, '+': 0}, {'cl': 0.1, '-': 0, '0': 1, '+': 0}, {'cl': -0.1, '-': 0, '0': 0, '+': 0}, {'cl': -0.4, '-': 1, '0': 1, '+': 1}, {'cl': -0.5, '-': 1, '0': 0, '+': 1}, {'cl': -0.8, '-': 1, '0': 2, '+': 0}, {'cl': -0.9, '-': 1, '0': 1, '+': 0}, {'cl': -1, '-': 1, '0': 0, '+': 0}, {'cl': -1.5, '-': 2, '0': 0, '+': 1}, {'cl': -1.9, '-': 2, '0': 1, '+': 0}, {'cl': -2, '-': 2, '0': 0, '+': 0}, {'cl': -3, '-': 3, '0': 0, '+': 0}]

# Calcula a media de uma serie de valores, usando uma potencia
def mean(values, power = 2):
	total = 0
	count = 0
	for v in values:
		count += 1
		total += float(math.pow(v, power))
	return math.pow(total / float(count), 1 / float(power))

# Substitui os valores em falta por um certo valor meanVote se replace == True
# Se replace == False, devolve a media normal
def meanReplace(values, power = 2, num = nBehaviours):
	tmp = values[:]
	if replace:
		for i in range(num - len(values)):
			tmp.append(meanVote)
	return mean(tmp, power)

# Calcula a media simples
def simpleMean(values):
	return mean(values, 1)

# Calcula a media harmonica
def harmonicMean(values):
	return mean(values, -1)

# Calcula a media quadratica
def quadraticMean(values):
	return mean(values, 2)

# Calcula a media das raizes quadradas
def sqrtMean(values):
	return mean(values, 0.5)

# Gera uma lista de nBehaviours notas, ordenados decrescentemente
# Com probabilidade hole, a nota e omitida
def generateRandom():
	values = list()
	for i in range(nBehaviours):
		if random.random() >= hole:
			values.append(random.randint(minVote, maxVote))	
	return sorted(values, reverse = True)

# Gera nGuys candidatos e suas notas para cada comportamento
def generateNRandom():
	random.seed()
	r = list()
	for i in range(nGuys):
		tmp = generateRandom()
		if tmp not in r:
			r.append(tmp)
	return r

# Calcula a media para uma lista de candidatos com votos 
def getAllMeans(valuesList, power):
	result = list()
	for values in valuesList:
		result.append({'list': values, 'mean': meanReplace(values, power)})

	return result

# Imprime as notas e respectiva cotacao para uma serie de candidatos
# Ordenados de forma decrescente
def printResults(results):
	
	tmp = sorted(results, key=lambda k: - k['mean'])
	for item in tmp:
		printLine(item)

# Imprime uma linha com notas e respectiva cotacao
def printLine(line):
	
	print "\t",
	count = 0
	for i in line['list']:
		count += 1
		print colored("  " + str(i), "blue"),
	for i in range(nBehaviours - count):
		print colored("  .", "blue"),
	print colored("\t" + ('%.2f' % line['mean']), "green")

# Compara varias listas
def printResultsComparing(results, others):

	tmp = sorted(results, key = lambda k: -k['mean'])
	
	printFirstLine(others.keys())
	for item in tmp:
		means = list()
		for other in others.values():
			mean = 0.0 
			for otherItem in other:
				if item['list'] == otherItem['list']:
					mean = otherItem['mean']
			means.append(mean)
		printLineComparing(item, means)

# Imprime a primeira linha quando se compara varias listas
def printFirstLine(names):
	print "\n\t",
	for i in range(nBehaviours):
		print colored(" #" + str(i+1), "blue"),
	print colored("\tres", "green"),
	for name in names:
		print colored("\t" + name, "yellow"),
	print "\n"

# Imprime uma linha com dados quando se compara varias listas
def printLineComparing(line, means):
	
	print "\t",
	count = 0
	for i in line['list']:
		count += 1
		print colored("  " + str(i), "blue"),
	for i in range(nBehaviours - count):
		print colored("  .", "blue"),
	print colored("\t" + ('%.2f' % line['mean']), "green"),
	for mean in means:
		print colored("\t" + ('%.2f' % mean), "yellow"),
	print

# Junta duas listas com medias
def combine(p0, p1):
	tmp = list()
	for p in p0:
		for q in p1:
			if q['list'] == p['list']:
				tmp.append({'list': p['list'], 'mean': p['mean'], 'compare': q['mean']})
	return tmp
		
# Compara duas listas e filtra os casos em que ha inversao de ordem
def filterEquals(p0, p1):

	pc = combine(p0, p1)
	result = list()
	for p in pc:
		inList = False
		for q in pc:
			if (p['mean'] - q['mean']) * (p['compare'] - q['compare']) < 0:
				inList = True
		if inList:
			result.append({'list': p['list'], 'mean': p['mean']})
		
	return result

# Compara n tipo de potencias, em que apenas os items que sao invertidos entre p0 e p1 sao aceites
def compareResults(p0, p1, ps):

	l = generateNRandom()
	t0 = getAllMeans(l, p0)
	t1 = getAllMeans(l, p1)
	ts = dict()
	for p in ps:
		name = '%.2f' % p
		ts[name] = getAllMeans(l, p)

	tf = filterEquals(t0, t1)
	name = '%.2f' % p1
	ts[name] = t1

	printResultsComparing(tf, ts)

# Compara resultados com e sem substituicao
def compareResultsReplacingOrNot(power):

	l = generateNRandom()
	global replace
	memory = replace
	replace = True
	t0 = getAllMeans(l, power)
	replace = False
	t1 = getAllMeans(l, power)
	replace = memory
	
	tf = filterEquals(t0, t1)
	ts = dict()
	ts['noRep'] = t1

	printResultsComparing(tf, ts)

# Gera todas as possiveis combinacoes de +, 0 e -
def generateAllGrades():

	grades = list()

	for i in range(nGrade + 1):
		for j in range(nGrade + 1):
			for k in range(nGrade + 1):
				if i + j + k <= nGrade:
					grades.append({'+': i, '0': j, '-': k})

	return grades

# Classifica um dado candidato baseado em monte de parametros
def classifyGrade(grade, passado, neutro, assimetria = 0.5):

	t = grade['+'] + grade['0'] + grade['-'] + passado
	r = grade['+'] + assimetria * grade['0'] + neutro 

	grade['cl'] = float(r) / float(t)

# Imprime as notas dum candidato
def printClassification(grade):
	
	tmp = 0
	print "\t",
	for i in range(0, grade['+']):
		print colored("#", "green"),
	tmp += grade['+']	
	for i in range(0, grade['0']):
		print colored("#", "yellow"),
	tmp += grade['0']	
	for i in range(0, grade['-']):
		print colored("#", "red"),
	tmp += grade['-']	
	for i in range(0, nGrade - tmp):
		print ".",
	if grade['cl'] < 0:
		print colored(" %.2f" % grade['cl'], "blue")
	else:
		print colored("  %.2f" % grade['cl'], "blue")

# Produz e imprime todas as possiveis classificacoes
def printAllClassifications(passado, neutro, assimetria = 1):

	grades = getAllClassifications(passado, neutro, assimetria)
	printClassifications(grades)

# Produz todas as possiveis classificacoes
def getAllClassifications(passado, neutro, assimetria = 0.5):

	grades = generateAllGrades()
	
	for grade in grades:
		classifyGrade(grade, passado, neutro, assimetria)

	return grades

# Imprime as classificacoes
def printClassifications(grades):
	tmp = sorted(grades, key=lambda g: - g['cl'])
	for grade in tmp:
		printClassification(grade)

# Inicializa todas as classificacoes com o numero de + menos o numero de -
def initializeAllGrades():
	grades = generateAllGrades()
	for grade in grades:
		grade['cl'] = grade['+'] - grade['-']
	return grades

# Utilitario para classificar a mao, ele imprime a lista completa
# Pergunta um a um, se queremos mudar
def classifyByHand(grades):

	printClassifications(grades)

	print 

	error = 0
	grades = sorted(grades, key=lambda g: - g['cl'])

	for grade in grades:
		printClassification(grade)
		try:
			cl = input("Nova classificacao: ")
			grade['cl'] = float(cl)
		except:
			error += 1

	return grades 

# Junta duas lista de notas (+, - e 0) com respectivas notas
def combineCl(g, h):

	result = list()
	for i in g:
		for j in h:
			if i['+'] == j['+'] and i['-'] == j['-'] and i['0'] == j['0']:
				result.append({'+': i['+'], '-': i['-'], '0': i['0'], 'cl': i['cl'], 'compare': j['cl']}) 
	return result

# Calcula a diferenca entre duas classifcacoes diferentes
def computeDifference(g0, g1):

	diff = 0
	count = 0
	gc = combineCl(g0, g1)
	for g in gc:
		for h in gc:
				tmp =(g['cl'] - h['cl']) * (g['compare'] - h['compare'])
				if tmp < 0:
					diff -= tmp
					count += 1

	printClassifications(g1)

	print colored("\tHouve " + str(count / 2) + " erros", "red")
	return diff

# Gera um novo candidato
def createRandomGuy():

	result = dict()

	possibleGrades = generateAllGrades()
	grade = random.choice(possibleGrades)

	grade['list'] = generateRandom()

	return grade

# Classifica um candidato	
def classifyRandomGuy(grade):

	passado = 3.3
	neutro = 2.2
	assimetria = 0.75

	classifyGrade(grade, passado, neutro, assimetria)

	power = 0.2

	grade['mean'] = (mean(grade['list'], power) - 1) / 5

	peso = 0.8

	grade['score'] = peso * grade['cl'] + (1 - peso) * grade['mean']

# Gere e classifica um gajo aleatoriamente
def createAndClassifyRandomGuy():

	grade = createRandomGuy()
	classifyRandomGuy(grade)

	return grade

# Gera nGuys candidatos e ordena pelo score
def createBunchOfGuys():

	grades = list()
	for i in range(nGuys):
		grades.append(createAndClassifyRandomGuy())

	grades = sorted(grades, key = lambda g: -g['score'])

	return grades

# Imprime a informacao final para cada candidato
def printRandomGuy(grade):

	count = 0
	print colored(("\t%.3f" % grade['score']) + "   ", "green"),
	for i in range(0, grade['+']):
		print colored("#", "green"),
	count += grade['+']	
	for i in range(0, grade['0']):
		print colored("#", "yellow"),
	count += grade['0']	
	for i in range(0, grade['-']):
		print colored("#", "red"),
	count += grade['-']	
	for i in range(0, nGrade - count):
		print ".",
	
	print colored("   " + ("%.3f" % grade['cl']) + "  ", "grey"), 

	count = 0
	for i in grade['list']:
		count += 1
		print colored(" " + str(i), "blue"), 
	for i in range(nBehaviours - count):
		print colored(" .", "blue"),

	print colored("   " + ("%.3f" % grade['mean']), "grey")

# Cria nGuys candidatos e classifica-os...
def main():
	random.seed()

	grades = createBunchOfGuys()
	print
	for grade in grades:
		printRandomGuy(grade)
