from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Profile


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(),
        }
        labels = {
            'avatar': _('Change avatar'),
        }
