from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q

from .models import TodoList


class UserAllowedRequiredMixin(LoginRequiredMixin, SuccessMessageMixin):
    model = None  # always set in the view
    success_message = None

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if not task.is_user_allowed(request.user):
            messages.error(request, "You don't have permissions to edit tasks. Please contact board administrator.")
            return render(request, 'forbidden.html')
        return super().dispatch(request, *args, **kwargs)


class BoardAdminRequiredMixin(LoginRequiredMixin):
    model = None  # always set in the view

    def dispatch(self, request, *args, **kwargs):
        board = get_board_from_kwargs(self.model, **kwargs)
        group_name = f"{board.title} admins"

        if request.user.groups.filter(name=group_name).exists() or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "Not enough privileges. Please contact board administrator.")
            return HttpResponseRedirect('/')


# TODO: refactor this mixin when roles are implemented
class BoardEditorRequiredMixin(LoginRequiredMixin):
    model = None  # always set in the view

    def dispatch(self, request, *args, **kwargs):
        board = get_board_from_kwargs(self.model, **kwargs)
        user = request.user

        # is_user_board_editor = bool(user_group_ids & allowed_group_ids) or user.is_superuser
        is_user_board_editor = TodoList.objects.filter(Q(pk=board.pk) & Q(allowed_users=user) | Q(owner=user)).exists()

        if not (is_user_board_editor or user.is_superuser):
            return render(request, template_name='forbidden.html')

        return super().dispatch(request, *args, **kwargs)


def get_board_from_kwargs(model, **kwargs):
    board_id = kwargs.get('pk', None)
    if board_id is None:
        raise ValueError("Board id (pk) not found in URL.")

    board = get_object_or_404(model, id=board_id)
    return board
