from django.shortcuts import HttpResponse, render
from .models import quiz as q, instructions, question, qtype
from courses.models import listener
from .forms import UserRegForm, UserLogForm, NewQuizForm, NewInstrForm
from .forms import NewQuestionForm, NewQuestionFormType
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views import generic
from django.contrib.auth.models import Group
from django import forms
from django.utils.datastructures import MultiValueDictKeyError
from .generator import gen as generator
import os, displayquizes
from django.conf import settings
from django.http import HttpResponse as httpr, Http404

#list of quizes is deprecated
def index(request):
	all_quizes = q.objects.all()
	context = {
		'all_quizes': all_quizes,
		'user': request.user,
	}
	if request.user.is_authenticated:
		return render(request, "displayquizes/index.html", context)
	else:
		return redirect("/login/")

#display one quiz (exam)
def quiz(request, quiz_id):
	quiz_data = q.objects.get(id=quiz_id)
	if request.user.groups.all().first().name == "student":
		try:
			listener.objects.get(user=request.user.id, course=quiz_data.course)
		except listener.DoesNotExist:
			return redirect("/forbidden/")
	all_instructions = instructions.objects.filter(Quiz=quiz_data)
	all_questions = question.objects.filter(Quiz=quiz_data)
	pth = os.path.dirname(displayquizes.__file__)
	file_exists = os.path.isfile(pth + "\\res\q" + str(quiz_id) + "\out.pdf")
	context = {
		'quiz_data': quiz_data,
		'all_instructions': all_instructions,
		'all_questions': all_questions,
		'user': request.user,
		'file_exists': file_exists,
	}
	if request.user.is_authenticated:
		return render(request, "displayquizes/quiz.html", context)
	else:
		return redirect("/login/")

#display page where you select type of question which 
#you want to add
def addq(request, quiz_id):
	all_types = qtype.objects.all()
	context = {
		'all_types': all_types,
		'user': request.user,
	}
	if request.user.is_authenticated:
		return render(request, "newquestion/index.html", context)
	else:
		return redirect("/login/")

#download exam file for quiz with quiz_id
def download(request, quiz_id):
	quiz_data = q.objects.get(id=quiz_id)
	if request.user.groups.all().first().name == "student":
		try:
			listener.objects.get(user=request.user.id, course=quiz_data.course)
		except listener.DoesNotExist:
			return redirect("/forbidden/")
	pth = os.path.dirname(displayquizes.__file__)
	file_path = os.path.join(pth, "res", "q" + str(quiz_id), "out.pdf")
	print(file_path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = httpr(fh.read(), content_type="application/vnd.ms-excel")
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
			return response
	else:
		raise Http404

#generate and process form for adding question to exam.
#Form fields depend on type of question.
#When form is posted, data from fields gets processed
#and then generic answer is written to model
class NewQuestionFormView(View):
	form_class = NewQuestionForm
	template_name = "newquestion/new.html" #

	#blank form
	def get(self, request, q_type, quiz_id):
		form = self.form_class(None)
		form.fields['Quiz'].queryset = q.objects.filter(id=quiz_id)
		if q_type in ["essay", "open"]:
			form.fields['Text'] = forms.CharField()
		elif q_type == "multchoice":
			it = q.objects.get(id=quiz_id).mcqaval
			cho = list()
			c = 1
			while c <= it:
				form.fields['Choice ' + str(c)] = forms.CharField()
				cho.append((str(c), str(c)))
				c += 1
			c = 1
			form.fields["Mark correct answer"] = forms.ChoiceField(choices=cho, widget=forms.RadioSelect())
		elif q_type == "manyanswers":
			it = q.objects.get(id=quiz_id).pcqaval
			cho = list()
			c = 1
			while c <= it:
				form.fields['Choice ' + str(c)] = forms.CharField()
				cho.append((str(c), str(c)))
				c += 1
			c = 1
			while c <= it:
				form.fields["Correct " + str(c)] = forms.BooleanField(required=False)
				c += 1
		elif q_type == "truefalse":
			cho = list()
			cho.append(("True", "True"))
			cho.append(("False", "False"))
			form.fields["True or false"] = forms.ChoiceField(choices=cho, widget=forms.RadioSelect())
		elif q_type == "match":
			c = 1
			while c <= 4:
				form.fields['Subquestion ' + str(c)] = forms.CharField()
				form.fields['Answer ' + str(c)] = forms.CharField()
				c += 1
			form.fields['Redundant answer'] = forms.CharField()
			
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request, q_type, quiz_id):
		if request.user.is_authenticated:
			if request.user.groups.all().first().name == "student":
				return redirect("/forbidden/")
		post = request.POST.copy()
		post['Type'] = qtype.objects.get(name=q_type).id
		form = NewQuestionFormType(post)
		if form.is_valid():
			saved = form.save()
			mod_q = question.objects.get(id=saved.pk)
			if q_type in ["essay", "open"]:
				mod_q.Answer = post['Text']
			if q_type == "multchoice":
				temp = ""
				it = q.objects.get(id=quiz_id).mcqaval
				c = 1
				corr = int(post['Mark correct answer'])
				while c <= it:
					if c == corr:
						temp += "True;"
					else:
						temp += "False;"
					temp += post["Choice " + str(c)] + ";"
					c += 1
				mod_q.Answer = temp
			elif q_type == "manyanswers":
				print(post)
				temp = ""
				it = q.objects.get(id=quiz_id).pcqaval
				c = 1
				while c <= it:
					try:
						post["Correct " + str(c)]
						temp += "2;"
					except MultiValueDictKeyError:
						temp += "-2;"
					temp += post["Choice " + str(c)] + ";"
					c += 1
				mod_q.Answer = temp
			elif q_type == "match":
				c = 1
				temp = ""
				while c <= 4:
					temp += post['Subquestion ' + str(c)] + ";"
					temp += post['Answer ' + str(c)] + ";"
					c += 1
				temp += ";" + post['Redundant answer'] + ";"
				mod_q.Answer = temp
			elif q_type == "truefalse":
				mod_q.Answer = post['True or false']
			mod_q.save()
			return redirect("/quizes/" + str(quiz_id) + "/")
		return render(request, self.template_name, {"f": form, 'user': request.user,})

#remove instruction from quiz
def rminstr(request, instr_id):
	instr_data = instructions.objects.get(id=instr_id)
	if request.user.is_authenticated:
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		instr_data.delete()
		return redirect("/quizes/" + str(instr_data.Quiz.id))
	else:
		return redirect("/login/")

#remove question from quiz
def rmquestion(request, ques_id):
	data = question.objects.get(id=ques_id)
	if request.user.is_authenticated:
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		data.delete()
		return redirect("/quizes/" + str(data.Quiz.id))
	else:
		return redirect("/login/")

#remove quiz from course
def rmquiz(request, quiz_id):
	data = q.objects.get(id=quiz_id)
	if request.user.is_authenticated:
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		data.delete()
		pth = os.path.dirname(displayquizes.__file__)
		os.remove(pth + "\\res\q" + str(quiz_id) + "\out.pdf")
		return redirect("/courses/")
	else:
		return redirect("/login/")

#create exam file for quiz
def make(request, quiz_id):
	data = q.objects.get(id=quiz_id)
	if request.user.is_authenticated:
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		pth = os.path.dirname(displayquizes.__file__)
		if os.path.isfile(pth + "\\res\q" + str(quiz_id) + "\out.pdf"):
			os.remove(pth + "\\res\q" + str(quiz_id) + "\out.pdf")
		if not os.path.isdir(pth + "\\res\q" + str(quiz_id)):
			os.makedirs(pth + "\\res\q" + str(quiz_id))
		generator.start(quiz_id)
		return redirect("/quizes/" + str(quiz_id))
	else:
		return redirect("/login/")

#new user registration form
class RegisterFormView(View):
	form_class = UserRegForm
	template_name = "register/register_form.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			username=form.cleaned_data['username']
			password=form.cleaned_data['password']
			user.set_password(password)
			user.save()
			Group.objects.get(name='student').user_set.add(user)

			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect("/")
		return render(request, self.template_name, {"f": form, 'user': request.user,})

#user login form
class LoginFormView(View):
	form_class = UserLogForm
	template_name = "register/login_form.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		form = self.form_class(request.POST)
		username=request.POST['username']
		password=request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect("/")
		return render(request, self.template_name, {"f": form, 'user': request.user,})

#form for creating new quiz (exam) in course
class NewQuizFormView(View):
	form_class = NewQuizForm
	template_name = "newquiz/new.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			if form.is_valid():
				quiz = form.save()
				quiz_mod = quiz
				quiz_mod.Author = request.user.username
				quiz_mod.save()
				return redirect("/quizes/" + str(quiz.id) + "/")
		return render(request, self.template_name, {"f": form, 'user': request.user,})

#form for creating new instruction in quiz
class NewInstrFormView(View):
	form_class = NewInstrForm
	template_name = "newinstr/new.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			if form.is_valid():
				instr = form.save()
				return redirect("/quizes/" + str(instr.Quiz.id) + "/")
		return render(request, self.template_name, {"f": form, 'user': request.user,})