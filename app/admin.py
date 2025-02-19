from django.contrib import admin
from .models import *


@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    pass


@admin.register(Messages)
class TasksAdmin(admin.ModelAdmin):
    list_display = ['messages_id']

@admin.register(SendMessageTask)
class TasksAdmin(admin.ModelAdmin):
    pass
