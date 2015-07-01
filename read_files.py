#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv

class read_file():

	global fileIn
	global fileOut
	
	def __init__(self, fileIn, fileOut):
		self.fileIn = fileIn
		self.fileOut = fileOut

	def read_file(self):
		f = open(self.fileIn, 'r')
		data = csv.reader(f, delimiter = ',', quotechar = '"')
		header = data.next()

		if (len(header) != 24):
			print "\tUnknown format!"
			return 0

		dimensions = list()
		questions = list()
		qMin = -1
		qMax = -1

		header = data.next()
		for i in range(len(header)):
			tmp = self.identifyQuestion(header[i])
			if tmp != None:
				if qMin == -1:
					qMin = i
				qMax = i
				dimensions.append(tmp)
				questions.append(header[i])

		for row in data:
			for i in range(qMin, qMax + 1):
				tmp = self.identifyAnswer(row[i])
				if tmp == None:
					print row[i]

	

	def identifyQuestion(self, frase):

		questions = dict()

		D0 = 'Comunicação'
		questions[D0] = list()
		questions[D0].append("A supplier, who you have a long relationship of trust with, tells you it is not possible to meet a deadline already agreed with the client. Would you:")
		questions[D0].append("You are in a team meeting to analyze a team's mistake. Would you:")
		questions[D0].append("A member of your team is always interrupting you with issues unrelated to work and this is affecting your productivity. Would you:")
		questions[D0].append("A new member to the team suggests a solution to a problem in the project that you find inadequate. Would you:")

		D1 = 'Relacionamento interpessoal'
		questions[D1] = list()
		questions[D1].append("A new member just joined your team, and another person is responsible for their integration. Would you:")
		questions[D1].append("You gave a task to a person, and later you realize that she is having trouble accomplishing it. Would you:")
		questions[D1].append("There is a team that has run into difficulties with a situation very similar to one that your team has already solved. Would you:")
		questions[D1].append("Someone from your team suggests for everyone to have lunch together, and you feel that there is a person who is not comfortable with the idea. Would you:")

		D2 = 'Recompensa'
		questions[D2] = list()
		questions[D2].append("Your team has successfully completed a highly profitable project. Despite having some financial problems, the organization intends to recognize this success. In your opinion:")
		questions[D2].append("You had a huge individual success in an important work, but few people at your organization recognize it. Would you:")
		questions[D2].append("Your contract is ending and you were called to discuss the future. Would you:")
		questions[D2].append("You are looking for a new job and you get three different proposals. Which one would you choose?")

		D3 = 'Desempenho'
		questions[D3] = list()
		questions[D3].append("You are in the middle of an important task when you are asked to perform a new urgent work for a very important but difficult customer. Would you:")
		questions[D3].append("A potential customer asks us for a pilot work to evaluate our performance. Would you:")
		questions[D3].append("You are starting a new long-term project. Would you:")
		questions[D3].append("After delivering a work to a client, you realize that you messed up. Would you:")


		D4 = 'Tomada de desição'
		questions[D4] = list()
		questions[D4].append("You find an error that for the moment does not seem to be a problem. Would you:")
		questions[D4].append("You are on a project, and you have arrived at a moment where you will have to make a strategic decision, for which you have the necessary competency and knowledge. Would you:")
		questions[D4].append("During a complicated phase of the project, one of your team members comes to ask you if he or she can exit the project. Would you:")
		questions[D4].append("A project you manage is delayed, and it is necessary to increase team productivity. Would you:")

		for d in questions:
			if frase in questions[d]:
				return d

		return None

	def identifyAnswer(self, frase):
		return 0	
