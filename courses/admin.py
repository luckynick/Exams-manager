from django.contrib import admin
from .models import listener, course, lecturer

# Register your models here.
admin.site.register(listener)
admin.site.register(course)
admin.site.register(lecturer)