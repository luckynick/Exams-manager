from .models import course, listener, lecturer
from django import forms
from django.contrib.auth.models import User


class NewCourseForm(forms.ModelForm):
	class Meta:
		model = course
		fields = ['name', 'description']

class NewListenerForm(forms.ModelForm):
	class Meta:
		model = listener
		fields = ['user', 'course']

class NewTeacherForm(forms.ModelForm):
	class Meta:
		model = lecturer
		fields = ['user', 'course']