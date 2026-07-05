from django.db import models
from django.conf import settings

#TODO: use django-guardian for more robust and enhanced permissions system (object level)
class TodoList(models.Model):
    class Meta:
        permissions = [
            ("create_board", "Allow user to create a board"),
            ("edit_board", "Allow user to edit board details"),
            ("delete_board", "Allow user to delete board"),
        ]

    title = models.CharField(max_length=150)
    description = models.CharField(max_length=200, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='allowed_boards', blank=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def is_user_allowed(self, user) -> bool:
        return user == self.owner or user in self.allowed_users.all() or user.is_superuser

    def show_delete_button(self, user) -> bool:
        return self.is_user_allowed(user)

class TodoItem(models.Model):
    class Meta:
        permissions = [
            ("create_task", "Allow user to add task"),
            ("edit_task", "Allow user to edit task details"),
            ("delete_task", "Allow user to delete task"),
        ]

    taskStatus = [
        ("NS", "Not started"),
        ("BL", "Blocked"),
        ("PR", "In Progress"),
        ("DN", "Done")
    ]
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 default=None,
                                 related_name="assignee")
    board = models.ForeignKey(TodoList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=taskStatus, default=taskStatus[0][0])
    high_priority = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def is_user_allowed(self, user) -> bool:
        return user == self.board.owner or user in self.board.allowed_users.all() or user.is_superuser
