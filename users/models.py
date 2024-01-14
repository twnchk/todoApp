from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(default='default.png', upload_to='avatars/')

    def __str__(self):
        return self.user.username
