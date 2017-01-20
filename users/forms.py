from .models import course
from django import forms


class NewCourseForm(forms.ModelForm):
	class Meta:
		model = course
		fields = ['name', 'description']