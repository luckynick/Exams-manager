from django.shortcuts import render, redirect
from courses.models import course, listener
from django.contrib.auth.models import User, Group

# Create your views here.

# display list of users
def index(request):
	all_users = User.objects.all()
	context = {
		'all_users': all_users,
		'user': request.user,
	}
	if request.user.is_authenticated:
		return render(request, "users/index.html", context)
	else:
		return redirect("/login/")

# display one user profile
def user_view(request, user_id):
	user_data = User.objects.get(id=user_id)
	all_listeners = listener.objects.filter(user=user_data)
	all_courses = course.objects.filter(pk__in=all_listeners.values_list('course', flat=True))
	context = {
		'user_data': user_data,
		'all_courses': all_courses,
		'user': request.user,
	}
	if request.user.is_authenticated:
		return render(request, "users/user.html", context)
	else:
		return redirect("/login/")

# remove user from other groups and add to teacher group
def make_teacher(request, user_id):
	user_data = User.objects.get(id=user_id)
	if request.user.is_authenticated:
		if request.user.groups.all().first().name != "admin":
			return redirect("/forbidden/")
		user_data.groups.clear()
		Group.objects.get(name='teacher').user_set.add(user_data)
		return redirect("/users/" + user_id)
	else:
		return redirect("/login/")