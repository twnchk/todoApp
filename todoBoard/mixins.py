from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


class LoginAndSuperUserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_superuser:
            return render(request, 'forbidden.html')

        return response
