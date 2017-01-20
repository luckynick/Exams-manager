"""exams URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from displayquizes.views import RegisterFormView, LoginFormView
from . import views

urlpatterns = [
    #/
	url(r'^$', views.index),
    #/admin/
    url(r'^admin/', admin.site.urls),
    #/quizes/
    url(r'^quizes/', include("displayquizes.urls")),
    #/courses/
    url(r'^courses/', include("courses.urls")),
    #/users/
    url(r'^users/', include("users.urls")),
    #/register/
    url(r'^register/', RegisterFormView.as_view()),
    #/login/
    url(r'^login/', LoginFormView.as_view()),
    #/logout/
    url(r'^logout/', views.logout_view),
    #/forbidden/
    url(r'^forbidden/', views.forbidden), 
]
