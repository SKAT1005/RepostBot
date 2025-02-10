from django.contrib import admin
from .models import Tasks


@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    pass
