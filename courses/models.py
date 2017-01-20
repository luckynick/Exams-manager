from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class course(models.Model):
	name = models.CharField(max_length=250)
	date = models.DateTimeField(auto_now_add=True, blank=True)
	description = models.CharField(max_length=1500)
	author = models.CharField(max_length=250)
	def __str__(this):
		return this.name

class listener(models.Model):
	course = models.ForeignKey(course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(this):
		return str(this.user) + " is listening " + str(this.course)

class lecturer(models.Model):
	course = models.ForeignKey(course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(this):
		return str(this.user) + " teaches " + str(this.course)