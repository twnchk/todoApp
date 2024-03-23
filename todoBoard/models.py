from users.models import CustomUser as User
from django.db import models
from django.contrib.auth.models import Group


class TodoList(models.Model):
    class Meta:
        permissions = [
            ("can_create_board", "Allow user to create a board"),
            ("can_view_board", "Allow user to view board"),
            ("can_delete_board", "Allow user to delete board"),
            ("can_edit_board", "Allow user to edit board details"),
        ]
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=200, null=True, blank=True)
    allowed_groups = models.ManyToManyField(Group, related_name='allowed_boards', blank=True)

    def __str__(self):
        return self.title


class TodoItem(models.Model):
    class Meta:
        permissions = [
            ("can_edit_task", "Allow user to edit task details"),
            ("can_delete_task", "Allow user to delete task"),
            ("can_create_task", "Allow user to add task"),
        ]
    taskStatus = [
        ("NS", "Not started"),
        ("BL", "Blocked"),
        ("PR", "In Progress"),
        ("DN", "Done")
    ]
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, default=None,
                                 related_name="assignee")
    board = models.ForeignKey(TodoList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=taskStatus, default=taskStatus[0])
    high_priority = models.BooleanField(default=False)

    def __str__(self):
        return self.name

