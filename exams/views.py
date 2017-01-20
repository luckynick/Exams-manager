from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth import logout


# Create your views here.

#redirect to list of courses if logged in.
#Give links to login and registration otherwise
def index(request):
	if request.user.is_authenticated:
		return redirect("/courses/")
	else:
		return HttpResponse("<a href='/login/'>Login</a><br>"
			+ "<a href='/register/'>Registration</a>")

#log user out
def logout_view(request):
    logout(request)
    return redirect("/")

#This page is displayed if user (mostly student) tries to 
#make some actions which are inappropriate considering permissions
def forbidden(request):
    return HttpResponse("This action is not allowed.<br>" 
    	+ "<a href='/'>Return to main page</a>")