from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, LoginForm
from .decorators import non_authenticated_only


# TODO: Create tests for these views and decorator
@non_authenticated_only
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('boards_list')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@non_authenticated_only
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('boards_list')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
