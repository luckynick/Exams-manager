from django.contrib import admin
from .models import quiz, question, instructions, qtype

# Register your models here.

admin.site.register(quiz)
admin.site.register(question)
admin.site.register(instructions)
admin.site.register(qtype)