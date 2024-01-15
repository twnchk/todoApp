from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import TodoItem, TodoList

admin.site.register(TodoList)
admin.site.register(TodoItem)
admin.site.register(Permission)
