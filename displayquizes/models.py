from django.db import models
from django.core.urlresolvers import reverse
from courses.models import course

#quiz (exam) in course
class quiz(models.Model):
	course = models.ForeignKey(course, on_delete=models.CASCADE)
	QuizName = models.CharField(max_length=250)
	QuizDate = models.DateTimeField(auto_now_add=True, blank=True)
	QuizDescription = models.CharField(max_length=1500)
	Author = models.CharField(max_length=250)
	mcqaval = models.IntegerField(default=4)
	pcqaval = models.IntegerField(default=4)
	def __str__(this):
		return this.QuizName

#instructions in quiz (exam)
class instructions(models.Model):
	Quiz = models.ForeignKey(quiz, on_delete=models.CASCADE)
	name = models.CharField(max_length=500)
	value = models.CharField(max_length=2500)
	def __str__(this):
		return this.name

#types of question
class qtype(models.Model):
	name = models.CharField(max_length=100)
	def __str__(this):
		return this.name

#question in quiz (exam)
class question(models.Model):
	Quiz = models.ForeignKey(quiz, on_delete=models.CASCADE)
	Type = models.ForeignKey(qtype, on_delete=models.CASCADE)
	Question = models.CharField(max_length=500)
	Answer = models.CharField(max_length=5000)
	def __str__(this):
		return this.Question