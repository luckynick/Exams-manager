from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import NewCourseForm, NewListenerForm, NewTeacherForm
from .models import course, lecturer, listener
from displayquizes.models import quiz
from django import forms
from django.contrib.auth.models import User
from django.forms.utils import ErrorList

# Create your views here.

#display list of all courses.
#Students see only courses on which they are enrolled.
def index(request):
	all_courses = course.objects.all()
	if request.user.groups.all().first().name == "student":
		all_listeners = listener.objects.filter(user=request.user)
		all_courses = course.objects.filter(pk__in=all_listeners.values_list('course', flat=True))
	context = {
		'all_courses': all_courses,
		'user': request.user,
	}
	if request.user.is_authenticated:
		return render(request, "courses/index.html", context)
	else:
		return redirect("/login/")

#Display course information
def course_view(request, course_id):
	course_data = course.objects.filter(id=course_id).first()
	if request.user.groups.all().first().name == "student":
		try:
			listener.objects.get(user=request.user.id, course=course_data)
		except listener.DoesNotExist:
			return redirect("/forbidden/")
	all_teachers = lecturer.objects.filter(course=course_data)
	all_listeners = listener.objects.filter(course=course_data)
	all_quizes = quiz.objects.filter(course=course_data)
	context = {
		'course_data': course_data,
		'all_quizes': all_quizes,
		'all_teachers': all_teachers,
		'all_listeners': all_listeners,
		'user': request.user,
	}
	if request.user.is_authenticated:
		return render(request, "courses/course.html", context)
	else:
		return redirect("/login/")

#Create new course
class NewCourseFormView(View):
	form_class = NewCourseForm
	template_name = "newcourse/new.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		new_course = self.form_class(request.POST)
		if new_course.is_valid():
			saved = new_course.save()
			mod_course = course.objects.get(id=saved.pk)
			mod_course.author = request.user.username
			mod_course.save()
			return redirect("/courses/")
		return render(request, self.template_name, {"f": form, 'user': request.user,})

#Add listener (student) to existing course
class NewListenerFormView(View):
	form_class = NewListenerForm
	template_name = "newlistener/new.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		new_course = self.form_class(request.POST)
		if new_course.is_valid():
			c = listener.objects.filter(course=new_course.cleaned_data['course'].id, 
				user=new_course.cleaned_data['user'].id)
			if c:
				return redirect("/courses/" + str(c.first().course.id))
			else:
				c = new_course.save()
				return redirect("/courses/" + str(c.course.id))

		return render(request, self.template_name, {"f": new_course, 'user': request.user,})

#Add teacher (lecturer) to existing course 
class NewTeacherFormView(View):
	form_class = NewTeacherForm
	template_name = "newlistener/new.html"

	#blank form
	def get(self, request):
		form = self.form_class(None)
		form.fields['user'].queryset = User.objects.filter(groups__name='teacher')
		return render(request, self.template_name, {"f": form, 'user': request.user,})

	#process form
	def post(self, request):
		if request.user.groups.all().first().name == "student":
			return redirect("/forbidden/")
		new_course = self.form_class(request.POST)
		if new_course.is_valid():
			c = listener.objects.filter(course=new_course.cleaned_data['course'].id, 
				user=new_course.cleaned_data['user'].id)
			if c:
				return redirect("/courses/" + str(c.first().course.id))
			else:
				if User.objects.filter(groups__name='teacher', 
					id=new_course.cleaned_data['user'].id):
					c = new_course.save()
					print("done")
					return redirect("/courses/" + str(c.course.id))
				else:
					errors = new_course._errors.setdefault("user", ErrorList())
					errors.append(u"User is not a teacher")

		return render(request, self.template_name, {"f": new_course, 'user': request.user,})