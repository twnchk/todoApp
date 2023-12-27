# Generated by Django 4.2.1 on 2023-12-27 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todoBoard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='todoitem',
            name='assignee',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='assignee', to=settings.AUTH_USER_MODEL),
        ),
    ]
