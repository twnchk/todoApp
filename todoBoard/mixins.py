from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages


class LoginAndSuperUserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_superuser:
            return render(request, 'forbidden.html')

        return response


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


class BoardEditorRequiredMixin(LoginRequiredMixin):
    model = None  # always set in the view

    def dispatch(self, request, *args, **kwargs):
        board = get_board_from_kwargs(self.model, **kwargs)
        user = request.user

        user_group_ids = set(user.groups.values_list('id', flat=True))
        allowed_group_ids = set(board.allowed_groups.values_list('id', flat=True))

        is_user_board_editor = bool(user_group_ids & allowed_group_ids) or user.is_superuser

        if not is_user_board_editor:
            return render(request, template_name='forbidden.html')

        return super().dispatch(request, *args, **kwargs)


def get_board_from_kwargs(model, **kwargs):
    board_id = kwargs.get('pk', None)
    if board_id is None:
        raise ValueError("Board id (pk) not found in URL.")

    board = get_object_or_404(model, id=board_id)
    return board
