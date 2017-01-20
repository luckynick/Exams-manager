from displayquizes.models import quiz, instructions, question, qtype
import re
import sys
import os.path as op
import string
import subprocess
import random
import displayquizes


oneChar = 0.02 #0.02

# This version of generator scrypt is adopted for database instead
# of XML file

def getQuizes(qid):
	''' From database'''
	questions_all = question.objects.filter(Quiz=qid)
	quizes = []
	for q in questions_all:
		nq = {}
		nq['Type'] = q.Type.name
		nq['Question'] = q.Question
		nq['Feedback'] = ""
		nq['Answer'] = q.Answer
		quizes.append(nq)
	return quizes

def getMeta(qid):
	''' Get all properties (quiz name, description, author). '''
	result = dict()
	meta = quiz.objects.get(id=qid)
	result["QuizName"] = meta.QuizName
	result["QuizDate"] = meta.QuizDate.strftime("%Y-%m-%d %H:%M")
	result["QuizDescription"] = meta.QuizDescription
	result["Author"] = meta.Author
	result["mcqaval"] = meta.mcqaval
	result["pcqaval"] = meta.pcqaval
	return result

def getInstructions(qid):
	''' Parses xml for instructions for working on test. Name of each instruction
	will be inserted to section name in latex document. There will be as many sections
	in Introduction part of document as number of properties in Instructions element
	in questions.xml '''
	desc = instructions.objects.filter(Quiz=qid)
	result = dict()
	for prop in desc:
		result[prop.name] =  prop.value
	return result

def makeInsertion(insertID, qid, seq_num):
	''' Returns latex insertion for provided insertID. 
	Works on questions.xml values. See commented sections in template.tex file 
	for examples. In parentheses of INSERTTAG you can see where 
	questions with special insertIDs will be located in final document'''
	quizes = getQuizes(qid)
	instr = getInstructions(qid)
	meta = getMeta(qid)
	insertion = "ERROR"
	if(insertID == "title"):
		insertion = meta["QuizName"]
	elif(insertID == "date"):
		insertion = meta["QuizDate"]
	elif(insertID == "author"):
		insertion = meta["Author"]
	elif(insertID == "author"):
		insertion = meta["Author"]
	elif(insertID == "intro"):
		insertion = "\chapter{Introduction}\n"
		for name, value in instr.items():
			insertion += "\section{" + name + "}\n"
			insertion += value + "\n"
	elif(insertID == "multchoice"):
		insertion = ""
		for quiz in quizes:
			if(quiz["Type"] == "multchoice"):
				insertion += "\\begin{question}[type=exam]\n"
				insertion += quiz["Question"] + "\n"
				insertion += "\\begin{enumerate}[a)]\n"
				answers = quiz["Answer"].split(";")
				answers.remove('')
				original = quiz["Answer"].split(";")
				random.shuffle(answers)
				true = ""
				for s in original:
					if(true == "True"):
						true = s
					if(s == "True"):
						true = s
						continue
					if(s == "False"):
						continue
				for s in answers:
					if(s == "True" or s == "False"):
						continue
					insertion += "\item " + s + "\n"
				insertion += "\end{enumerate}\n\end{question}\n\\begin{solution}\n"
				insertion += true + "\n" + "\end{solution}\n"

	elif(insertID == "truefalse"):
		insertion = ""
		for quiz in quizes:
			if(quiz["Type"] == "truefalse"):
				insertion += "\\begin{question}[type=exam]\n"
				insertion += quiz["Question"] + "\\\\\n"
				insertion += "T) True\\\\ \nF) False\n"
				true = quiz["Answer"]
				insertion += "\end{question}\n\\begin{solution}\n"
				insertion += true + "\n" + "\end{solution}\n"
	elif(insertID == "match"):
		insertion = ""
		for quiz in quizes:
			if(quiz["Type"] == "match"):
				list_m = quiz["Answer"].split(";");
				matches = dict(zip(list_m[0::2], list_m[1::2]))
				keys = list(matches.keys())
				values = list(matches.values())
				random.shuffle(keys)
				random.shuffle(values)
				insertion += "\\begin{question}[type=exam]\n"
				insertion += quiz["Question"] + "\\\\\n"
				insertion += "\\begin{minipage}{0.45\\textwidth}\n\\begin{enumerate}\n"
				for left in keys:
					if(left == ""):
						continue
					insertion += "\item " + left + "\n"
				insertion += "\end{enumerate}\n\end{minipage}\n\hfill\n\\begin{minipage}{0.45\\textwidth}\n"
				insertion += "\\begin{tabular}{|p{\\textwidth}}\n\\begin{enumerate}[a)]\n"
				for right in values:
					if(right == ""):
						continue
					insertion += "\item " + right + "\n"
				insertion += "\end{enumerate}\n\end{tabular}\n\end{minipage}\n\end{question}\n\\begin{solution}\n"
				for left, right in matches.items():
					if(left == "" or right == ""):
						continue
					insertion += left + " corresponds to " + right + ", "
				insertion = insertion.strip(", ")
				insertion += "\n\end{solution}"
	elif(insertID == "manyanswers"):
		insertion = ""
		for quiz in quizes:
			if(quiz["Type"] == "manyanswers"):
				insertion += "\\begin{question}[type=exam]\n"
				insertion += quiz["Question"] + "\\\\\n"
				insertion += "\\begin{enumerate}[a)]\n"
				answers = quiz["Answer"].split(";")
				answers.remove('')
				right = ""
				nextTrue = False
				for s in answers:
					try:
						temp = int(s)
						if(temp > 0):
							nextTrue = True
					except ValueError:
						if(nextTrue == True):
							right += s + ", "
							nextTrue = False
				random.shuffle(answers)
				for s in answers:
					try:
						temp = int(s)
					except ValueError:
						insertion += "\item " + s + "\n"
				right = right.strip(", ")
				insertion += "\end{enumerate}\n\end{question}\n\\begin{solution}\n"
				insertion += right + " are right answers\n" + "\end{solution}\n"
	elif(insertID == "open"):
		insertion = ""
		for quiz in quizes:
			if(quiz["Type"] == "open"):
				insertion += "\\begin{question}[type=exam]\n" + quiz["Question"]
				insertion += "\\\\\n\end{question}\n\setstretch{2}{\\blank[width=" 
				insertion += str(len(quiz["Answer"]) * oneChar) + "\linewidth]{}~\\\\ \n}"
				insertion += "\\begin{solution}\n" + quiz["Answer"] + "\n\end{solution}\n"
	elif(insertID == "essay"):
		insertion = ""
		for quiz in quizes:
			if(quiz["Type"] == "essay"):
				insertion += "\\begin{question}[type=exam]\n" + quiz["Question"]
				insertion += "\\\\\n\end{question}\n\setstretch{2}{\\blank[width=" 
				insertion += str(len(quiz["Answer"]) * oneChar) + "\linewidth]{}~\\\\ \n}"
				insertion += "\\begin{solution}\n" + quiz["Answer"] + "\n\end{solution}\n"
	elif(insertID == "multchoiceAHint"):
		insertion = "\hspace{30pt} "
		c = 0
		symb = ord('a')
		while c < int(meta["mcqaval"]):
			insertion += str(chr(symb + c)) + "\hspace{3pt} "
			c += 1
	elif(insertID == "multchoiceAns"):
		lim = que_count["multchoice"]
		c = 0
		insertion = ""
		while c < lim:
			insertion += "\item \\fbox{\n"
			g = 0
			while g < int(meta["mcqaval"]):
				insertion += "\mbox{\ooalign{$\square$}} "
				g += 1
			insertion += "\n}\n"
			c += 1
	elif(insertID == "truefalseAns"):
		lim = int(que_count["truefalse"])
		c = 0
		insertion = ""
		while c < lim:
			insertion += "\item \\fbox{\mbox{\ooalign{$\square$}} \mbox{\ooalign{$\square$}}}\n"
			c += 1
	elif(insertID == "matchAns"):
		lim = int(que_count["match"])
		insertion = ""
		c = 0
		while c < lim:
			insertion += "\item \\fbox{\n\\begin{minipage}{10em}\n\hspace{22pt}"
			insertion += " a\hspace{3pt} b\hspace{3pt} c\hspace{3pt} d\hspace{3pt} e\n"
			insertion += "\\begin{enumerate}[1]\n\itemsep0em\n\setcounter{enumi}{0}\n"
			k = 0
			while k < 4:
				insertion += "\item \mbox{\ooalign{$\square$}} \mbox{\ooalign{$\square$}} "
				insertion += "\mbox{\ooalign{$\square$}} \mbox{\ooalign{$\square$}} "
				insertion += "\mbox{\ooalign{$\square$}}\n"
				k += 1
			insertion += "\end{enumerate}\n\end{minipage}\n}\n"
			insertion += "\setcounter{enumi}{" + str(seq_num + c - 1) + "}\n"
			c += 1
	elif(insertID == "manyanswersAHint"):
		insertion = "\hspace{25pt} "
		c = 0
		symb = ord('a')
		while c < int(meta["pcqaval"]):
			insertion += str(chr(symb + c)) + "\hspace{3pt} "
			c += 1
		insertion += "\n"
		insertion += "\setcounter{enumi}{" + str(seq_num + c) + "}\n"
	elif(insertID == "manyanswersAns"):
		insertion = ""
		lim = int(que_count["manyanswers"])
		c = 0
		while c < lim:
			insertion += "\item \\fbox{"
			g = 0
			while g < int(meta["pcqaval"]):
				insertion += "\mbox{\ooalign{$\square$}} "
				g += 1
			insertion += "}\n"
			c += 1
	elif(insertID == "openAns"):
		insertion = ""
		lim = int(que_count["open"])
		c = 0
		lengths = countAnsLength(qid, "open")
		if lengths:
			insertion = "\\begin{enumerate} \setstretch{2}{"
			while c < lim:
				insertion += "\item{\\blank[width=" 
				insertion += str(lengths.pop(0) * oneChar) + "\linewidth]{}~\\\\ \n}\n"
			c += 1
			insertion += "} \end{enumerate}"
	elif(insertID == "essayAns"):
		insertion = ""
		lim = int(que_count["essay"])
		c = 0
		lengths = countAnsLength(qid, "essay")
		while c < lim and lengths:
			insertion += "\\blank[width=" + str(lengths.pop(0) * oneChar) +"\linewidth]{}~\\"
			c += 1

	return insertion

def genTex(template, qid):
	''' Creates new latex document from template.
	Template contains %INSERTTAG(insertID). Newly created document will
	contain insertions from questions.xml on place of INSERTTAG. '''
	global que_count
	que_count = countQues(qid)
	insertType = "None"
	outTex = "";
	pattern = re.compile("%INSERTTAG\((.+)\)")
	c = 0
	for line in template:
		found = pattern.search(line)
		if found is not None:
			insertID = found.group(1)
			if("Ans" in insertID):
				outTex += "\setcounter{enumi}{" + str(c) + "}\n"
				c += que_count[insertID.replace("Ans", "")]
			outTex += makeInsertion(found.group(1), qid, c)
		else:
			outTex += line
	return outTex;

def countQues(qid):
	''' Counts number of every type of questions, returns dict where
	type of question is a key '''
	types = qtype.objects.all()
	counts = dict()
	type = ""
	for t in types:
		counts[t.name] = question.objects.filter(Type=t, Quiz=qid).count()
	return counts

def countAnsLength(qid, type):
	''' Count lengths of answers and put each of them to list '''
	ty = qtype.objects.get(name=type).id
	struc = question.objects.filter(Type=ty, Quiz=qid)
	counts = list()
	for field in struc:
		counts.append(len(field.Answer))
	return counts


def start(qid):
	qid = int(qid)
	pth = op.dirname(displayquizes.__file__)
	templ_path = "\generator\\templ.tex"
	out_tex_path = "\generator\out.tex"
	file_in = open(pth + templ_path, "r")
	templ_content = file_in.readlines()
	file_in.close()
	tex = genTex(templ_content, qid)
	out_tex = open(pth + out_tex_path, "w")
	out_tex.write(tex)
	out_tex.close()
	try:
		subprocess.check_call(['pdflatex', "-output-directory=" + pth + "\\res\q" + str(qid), pth + out_tex_path])
	except Exception:
		print("There was error in pdflatex")