# Generated by Django 4.2.1 on 2024-03-23 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todoBoard', '0009_adjust_existing_group_names'),
    ]

    operations = [
        migrations.RenameField(
            model_name='todoitem',
            old_name='category',
            new_name='board',
        ),
    ]