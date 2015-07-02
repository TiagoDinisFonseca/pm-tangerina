#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
from termcolor import colored

class read_file():

	global fileIn
	global fileOut
	
	def __init__(self, fileIn, fileOut):
		self.fileIn = fileIn
		self.fileOut = fileOut

	def main(self):
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

		failed = 0

		guys = list()
		for row in data:
			guy = list()
			for i in range(qMin, qMax + 1):
				tmp = self.identifyAnswer(row[i])
				if tmp == None:
					print colored("Erro: string não reconhecida: ", "red"), row[i]
					return
				else: 
					guy.append(tmp)
			guys.append(guy)

		g = open(self.fileOut, 'w')
		output = csv.writer(g, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_NONNUMERIC)

		output.writerow(dimensions)
		output.writerow(questions)
		for guy in guys:
			output.writerow(guy)
	
		f.close()
		g.close()
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


		D4 = 'Tomada de decisão'
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

		answers = dict()
		# Comunicação
		B00 = 'Tolerância'
		answers[B00] = list()
		answers[B00].append("Try to manage the reaction of the team facing the error, accepting the various sentiments expressed by the different members?")
		answers[B00].append("Accept the supplier's situation and try to renegotiate the deadline with the client?")
		B01 = 'Empatia'
		answers[B01] = list()
		answers[B01].append("Schedule a meeting with the supplier so you can better understand the situation, and together find a solution?")
		answers[B01].append("Try to look at the problem from a new perspective, because you know that a new member can bring new findings?")
		answers[B01].append("Try to understand why the person needs to speak to you?")
		B02 = 'Assertividade'
		answers[B02] = list()
		answers[B02].append("Explain that you need silence to concentrate, and thank him/her for understanding your needs?")
		answers[B02].append("Say that the solution is not good, and guide him/her with the experience you have in the project?")
		answers[B02].append("Explain your commitment assertively, and give a deadline to the supplier to present a viable solution?")
		B03 = 'Objetividade'
		answers[B03] = list()
		answers[B03].append("Try to explain your point of view simply and clearly?")
		answers[B03].append("Ask him to stop talking and to concentrate on his/her work?")
		B04 = 'Escuta ativa'
		answers[B04] = list()
		answers[B04].append("Try to better understand the solution he/she proposed, clarifying the details, in order to form a consistent opinion?")
		answers[B04].append("Try to structure what is discussed in the meeting, in order to present a clear summary?")

		# Relacionamento interpessoal
		B10 = 'Ser apoiante'
		answers[B10] = list()
		answers[B10].append("Offer to help the new member when necessary?")
		answers[B10].append("Propose to get someone on the task who can help?")
		B11 = 'Colaboração'
		answers[B11] = list()
		answers[B11].append("Offer yourself to look for a restaurant that is good for everyone to talk freely?")
		answers[B11].append("Join the other team and help solve problems?")
		answers[B11].append("Try to do tasks together with the new member?")
		B12 = 'Liderança'
		answers[B12] = list()
		answers[B12].append("Challenge your team to collaborate with the other team to overcome the situation?")
		answers[B12].append("Motivate the person who is not comfortable, and remind him/her of the importance of the team to be all together?")
		answers[B12].append("Work something out so that the new member receives the optimal task to start?")
		B13 = 'Partilha aberta de informação'
		answers[B13] = list()
		answers[B13].append("Share your solution and all relevant information?")
		answers[B13].append("Give more information to the person, sharing your experience of what works and what does not work in these types of task?")
		B14 = 'Orientado para pessoas'
		answers[B14] = list()
		answers[B14].append("Propose to the person to begin with a simpler task to gain more experience?")
		answers[B14].append("Refuse the invitation, and invite the person who was uncomfortable with the suggestion, to have lunch just the two of you?")

		# Recompensa
		B20 = 'Pagamento mais elevado por bons desempenhos'
		answers[B20] = list()
		answers[B20].append("Prefer to receive a monetary bonus?")
		answers[B20].append("There should be a bonus distributed according to the performance evaluations of each team member.")
		B21 = 'Equidade'
		answers[B21] = list()
		answers[B21].append("The company where salaries are fair and proportional?")
		answers[B21].append("Ask that you be renewed with a contract under the same terms as people who have similar responsibilities to your own?")
		answers[B21].append("There should be an equal bonus for all the team members, because everyone contributed to the success of the project.")
		B22 = 'Segurança no emprego'
		answers[B22] = list()
		answers[B22].append("The company should not distribute any bonus, and should use that money to solve their financial problems.")
		answers[B22].append("Accept to maintain your current job functions, but ask that you receive a permanent contract?")
		answers[B22].append("The company where there is high job security?")
		B23 = 'Oportunidade para crescimento pessoal'
		answers[B23] = list()
		answers[B23].append("Prefer to be assigned new responsibilities to help you grow professionally?")
		answers[B23].append("Accept to renew your contract for another six months, but ask that you be given new challenges that allow you to grow within the organization?")
		B24 = 'Reconhecimento e valorização por bom desempenho'
		answers[B24] = list()
		answers[B24].append("Prefer that people you work with recognize your success and value it?")
		answers[B24].append("The company that recognizes and appreciates people's good performance?")

		# Desempenho
		B30 = 'Orientado para resultados'
		answers[B30] = list()
		answers[B30].append("Try hard to meet the deadline, being available to work overtime?")
		answers[B30].append("Put all your effort in fulfilling the goals set by the customer?")
		B31 = 'Criatividade'
		answers[B31] = list()
		answers[B31].append("Use time to find a creative solution for the urgent work, at the risk of the work not being adequate?")
		answers[B31].append("Take advantage to try several different approaches in search of an optimal solution, even though you may not find one?")
		answers[B31].append("Inform the client, because you know that a blunder is an opportunity for new perspectives?")
		B32 = 'Gestão de stress'
		answers[B32] = list()
		answers[B32].append("Work to identify from the beginning any evidence of problems, in order to protect the team from stress throughout the project?")
		answers[B32].append("Inform the client and the team, so that the problem is solved as soon as possible?")
		answers[B32].append("Accept the impossibility of the conflicting priorities, and ask for help to solve the situation?")
		B33 = 'Elevadas expetativas de desempenho'
		answers[B33] = list()
		answers[B33].append("Work hard to ensure that, from day one, everything is run according to best practices, even though this may delay the project?")
		answers[B33].append("Guide your efforts to develop a work that brings value to the customer?")
		B34 = 'Competitividade'
		answers[B34] = list()
		answers[B34].append("Set yourself to the task so that it exceeds the solutions proposed by the competition?")
		answers[B34].append("Try to solve the problem without anyone noticing?")

		# Tomada de decisão
		B40 = 'Autonomia'
		answers[B40] = list()
		answers[B40].append("Use some of your time to investigate the origin of the error?")
		answers[B40].append("Decide according to your experience and your principles, simplifying the decision-making process?")
		B41 = 'Iniciativa e pragmatismo'
		answers[B41] = list()
		answers[B41].append("Ask for him to remain on the project during this difficult phase, and ask him 	to come back to speak about leaving later?")
		answers[B41].append("Join the team yourself, and work extra hours to ensure on-time delivery?")
		answers[B41].append("Propose to the team to solve the error quickly?")
		B42 = 'Adaptabilidade'
		answers[B42] = list()
		answers[B42].append("Register and document the error so that the team can decide which is the best strategy to follow?")
		answers[B42].append("Agree with the person to work half-time on the project, so the team can adapt to the new reality?")
		answers[B42].append("Focus the team on the problem, requiring extra effort from each member, so 	that you all can adapt to the situation?")
		B43 = 'Gestão de risco'
		answers[B43] = list()
		answers[B43].append("Consult as many people as possible, and from their opinions think about the benefits and risks of each option?")
		answers[B43].append("Consult the various team members, think about the various opinions, and decide based on that information?")
		B44 = 'Assumir responsabilidade individual'
		answers[B44] = list()
		answers[B44].append("Bring back a former team member, accepting that you will reduce your bonus indexed to the profit margin of the project?")
		answers[B44].append("Consult the people involved, but it is ultimately up to you to make the  	decision and assume the responsibility?")

		for a in answers:
			if frase.strip() in answers[a]:
				return a
		return None	
