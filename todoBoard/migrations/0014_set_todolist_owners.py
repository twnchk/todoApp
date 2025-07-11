# Generated by Django 4.2.1 on 2025-06-08 15:50

from django.db import migrations

def set_todolist_owners(apps, schema_editor):
    TodoList = apps.get_model('todoBoard', 'TodoList')
    User = apps.get_model('users', 'CustomUser')
    TodoItem = apps.get_model('todoBoard', 'TodoItem')

    for board in TodoList.objects.all():
        related_tasks = TodoItem.objects.filter(board=board)
        if related_tasks.exists():
            board.owner = related_tasks.first().author
        else:
            board.owner = User.objects.first()
        board.save()

def reverse_set_todolist_owners(apps, schema_editor):
    TodoList = apps.get_model('todoBoard', 'TodoList')
    for board in TodoList.objects.all():
        board.owner = None
        board.save()


class Migration(migrations.Migration):

    dependencies = [
        ('todoBoard', '0013_remove_todolist_allowed_groups_and_more'),
    ]

    operations = [
        migrations.RunPython(set_todolist_owners, reverse_set_todolist_owners),
    ]
