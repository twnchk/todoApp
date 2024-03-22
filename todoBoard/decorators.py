from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from functools import wraps


def task_editor_required(view):
    def wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name="Task editors").exists():
            return view(request, *args, **kwargs)
        else:
            error_msg = "Not enough privileges. Please contact board administrator."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=403)
            else:
                # Actually probably will never be used.. todo delete?
                messages.error(request, error_msg)
                return HttpResponseRedirect('/')
    return wrapped_view


def is_user_in_allowed_group_for_board(user, board):
    user_groups = user.groups.all()
    allowed_groups = board.allowed_groups.all()

    if not (user_groups and allowed_groups).exists():
        return False
    return True


def board_editor_required(model):
    def decorator(view):
        @wraps(view)
        def wrapped_view(request, *args, **kwargs):
            board_id = kwargs.pop('board_id', None)
            if board_id is None:
                raise ValueError("Board id not found in URL")

            board = get_object_or_404(model, id=board_id)

            if not is_user_in_allowed_group_for_board(request.user, board):
                return render(request, template_name='forbidden.html')

            return view(request, board_id, *args, **kwargs)
        return wrapped_view
    return decorator


def board_admin_required(model):
    def decorator(view):
        @wraps(view)
        def wrapped_view(request, *args, **kwargs):
            board_id = kwargs.pop('board_id', None)
            if board_id is None:
                raise ValueError("Board id not found in URL")

            board = get_object_or_404(model, id=board_id)
            if request.user.groups.filter(name="Board admins").exists():
                return view(request, board_id, *args, **kwargs)
            else:
                messages.error(request, "Not enough privileges. Please contact board administrator.")
                return HttpResponseRedirect('/')
        return wrapped_view
    return decorator
