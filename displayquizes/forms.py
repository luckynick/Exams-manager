from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import quiz, question, instructions

#form for registration
class UserRegForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

#form for login
class UserLogForm(AuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

#form for adding new quiz
class NewQuizForm(forms.ModelForm):
    mcqaval = forms.IntegerField(label="Number of ans. in mult. choice with one correct answer", 
        initial=4)
    pcqaval = forms.IntegerField(label="Number of ans. in mult. choice with many correct answer", 
        initial=4)
    class Meta:
        model = quiz
        fields = ['course', 'QuizName', 'QuizDescription', 'mcqaval', 'pcqaval']

#form for adding new instruction
class NewInstrForm(forms.ModelForm):
    class Meta:
        model = instructions
        fields = ['Quiz', 'name', 'value']

#Base of form for adding question.
#User will see full form generated depending on
#question type.
class NewQuestionForm(forms.ModelForm):

    class Meta:
        model = question
        fields = ['Quiz', 'Question']

#extended version of form.
#Type field sholdn't be set by user because 
#form structure is dependant on type of question.
#Project doesn't have dynamic pages.
#But type field is obligatory because it is NOT NULL.
#So this field is set on server side after form is posted.
class NewQuestionFormType(forms.ModelForm):

    class Meta:
        model = question
        fields = ['Quiz', 'Question', 'Type']