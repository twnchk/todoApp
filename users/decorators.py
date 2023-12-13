from django.shortcuts import redirect


def non_authenticated_only(view):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('boards_list')
        return view(request, *args, **kwargs)
    return wrapped_view
