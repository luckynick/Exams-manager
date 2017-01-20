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
from django.conf.urls import url
from . import views
from .views import NewQuizFormView, NewInstrFormView, NewQuestionFormView

urlpatterns = [
    #/quizes/ #list of quizes is irrelevant
    #url(r'^$', views.index, name='index'),
    #/quizes/add/
    url(r'^add/', NewQuizFormView.as_view()),
    #/quizes/*num*/rm/
    url(r'^(?P<quiz_id>[0-9]+)/rm', views.rmquiz),
    #/quizes/*num*/
    url(r'^(?P<quiz_id>[0-9]+)/$', views.quiz, name='quiz'),
    #/quizes/questions/*num*/
    url(r'^questions/(?P<question_id>[0-9]+)/', NewQuizFormView.as_view()),
    #/quizes/addinstr/
    url(r'^addinstr/', NewInstrFormView.as_view()),
    #/quizes/*num*/addquestion/
    url(r'^(?P<quiz_id>[0-9]+)/addquestion/$', views.addq),
    #/quizes/*num*/addquestion/*str*/
    url(r'^(?P<quiz_id>[0-9]+)/addquestion/(?P<q_type>[a-zA-Z]+)/$', NewQuestionFormView.as_view()),
    #/quizes/rminstr/*num*/
    url(r'^rminstr/(?P<instr_id>[0-9]+)/', views.rminstr),
    #/quizes/rmquestion/*num*/
    url(r'^rmquestion/(?P<ques_id>[0-9]+)/', views.rmquestion),
    #/quizes/*num*/make/
    url(r'^(?P<quiz_id>[0-9]+)/make/$', views.make),
    #/quizes/*num*/download/
    url(r'^(?P<quiz_id>[0-9]+)/download/$', views.download),
]
