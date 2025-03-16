import json

from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# Views
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, View, DeleteView

# Mixins
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import BoardAdminRequiredMixin, BoardEditorRequiredMixin, TaskEditorRequiredMixin

# Models
from .models import TodoList, TodoItem
from users.models import CustomUser

# Forms
from .forms import CreateTaskForm, CreateBoardForm


class IndexView(TemplateView):
    template_name = 'index.html'


# Board views
class AllBoardsListView(LoginRequiredMixin, ListView):
    model = TodoList
    context_object_name = 'boards'
    template_name = 'boards.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return render(request, 'forbidden.html')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        for board in queryset:
            board.show_delete_button = board.show_delete_button(self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_header'] = "All boards: "
        return context


class UserBoardsListView(LoginRequiredMixin, ListView):
    model = TodoList
    context_object_name = 'boards'
    template_name = 'boards.html'

    def get_queryset(self):
        boards = super().get_queryset()
        user = self.request.user
        return boards.filter(Q(allowed_groups__in=user.groups.all()) | Q(pk=user.pk)).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_header'] = f"{user} boards: "

        for board in context['boards']:
            board.show_delete_button = board.show_delete_button(user)

        return context


class ArchivedBoardsList(LoginRequiredMixin, ListView):
    model = TodoList
    context_object_name = 'boards'
    template_name = 'archived_boards.html'

    def get_queryset(self):
        boards = super().get_queryset()
        user = self.request.user

        for board in boards:
            board.show_delete_button = board.show_delete_button(user)

        if user.is_superuser:
            return boards.filter(Q(is_archived=True))

        return boards.filter(Q(allowed_groups__in=user.groups.all()) & Q(is_archived=True)).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        for board in context['boards']:
            board.show_delete_button = board.show_delete_button(user)

        return context


class BoardDetailView(LoginRequiredMixin, DetailView):
    model = TodoList
    context_object_name = 'board'
    template_name = 'board_detail.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        board = self.get_object()
        if not board.is_user_allowed(request.user):
            return render(request, 'forbidden.html')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = TodoItem.objects.filter(board=self.object)
        return context

    def get_template_names(self):
        board = self.get_object()
        if board.is_archived:
            return ['board_detail_archive.html']
        return [self.template_name]


class BoardBacklogView(BoardDetailView):
    def get_template_names(self):
        return ['board_backlog.html']


class BoardCreateView(LoginRequiredMixin, CreateView):
    model = TodoList
    form_class = CreateBoardForm
    template_name = "create_board.html"

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        form = self.form_class
        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            new_board_group_name = form.cleaned_data['title'] + ' admins'
            new_group, created = Group.objects.get_or_create(name=new_board_group_name)

            if created:
                board_content_type = ContentType.objects.get_for_model(TodoList)
                task_content_type = ContentType.objects.get_for_model(TodoItem)
                board_permissions = Permission.objects.filter(content_type=board_content_type)
                task_permissions = Permission.objects.filter(content_type=task_content_type)

                new_group.permissions.add(*board_permissions)
                new_group.permissions.add(*task_permissions)
                request.user.groups.add(new_group)

                new_board = form.save()
                new_board.allowed_groups.add(new_group)

                return redirect('board_detail', pk=new_board.pk)
            else:
                form.add_error(None, 'A group with this name already exists.')
        return render(request, self.template_name, context={'form': form})


class BoardUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'GET method is not allowed for this action'}, status=405)

    def post(self, request, pk, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid request.'})

        board = get_object_or_404(TodoList, pk=pk)
        body_unicode = request.body.decode("utf-8")
        json_data = json.loads(body_unicode)
        board_title = json_data.get('boardTitle')
        board_description = json_data.get('boardDescription')

        board.title = board_title
        board.description = board_description

        with transaction.atomic():
            board.save()

        return JsonResponse({'success': True, 'message': 'Board updated successfully.'})


class BoardDeleteView(BoardAdminRequiredMixin, DeleteView):
    model = TodoList
    success_url = reverse_lazy('boards_list')

    def get(self, request, *args, **kwargs):
        # Prevent accidental deletion through GET requests
        return HttpResponseRedirect('/')


class BoardCloseView(BoardEditorRequiredMixin, View):
    model = TodoList

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'GET method is not allowed for this action'}, status=405)

    def post(self, request, *args, **kwargs):
        board_id = kwargs.pop("pk", None)
        board = get_object_or_404(TodoList, pk=board_id)

        # Mark all tasks as done when board is closed
        for task in board.todoitem_set.all():
            if task.status != "DN":
                task.status = "DN"
                task.save()
        board.is_archived = True
        board.save()
        return JsonResponse({'success': True, 'message': 'Board closed successfully.'})


class BoardRepoenView(BoardEditorRequiredMixin, View):
    model = TodoList

    def post(self, request, *args, **kwargs):
        board_id = kwargs.pop("pk", None)
        board = get_object_or_404(TodoList, pk=board_id)
        board.is_archived = False
        board.save()
        return redirect('board_detail', pk=board_id)


# Task views
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = TodoItem
    form_class = CreateTaskForm
    template_name = "create_task.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        board_id = self.kwargs.get("board_id")

        kwargs.update({
            'init_board_id': board_id,
            'user_id': self.request.user.id,
        })

        return kwargs

    def get_success_url(self):
        board_id = self.kwargs.get('board_id')
        if not board_id:
            raise ValueError('ID not provided in the URL')
        return reverse('board_detail', kwargs={'pk': board_id})

    def form_valid(self, form):
        response = super().form_valid(form)
        task_name = form.cleaned_data['name']
        messages.success(self.request, f'Task "{task_name}" has been created.')
        return response


class TaskChangeStatusView(TaskEditorRequiredMixin, UpdateView):
    model = TodoItem

    def post(self, request, *args, **kwargs):
        task_id = request.POST.get("task_id")
        new_status = request.POST.get("new_status")
        task = get_object_or_404(TodoItem, id=task_id)
        if not task.board.is_archived:
            task.status = new_status
            with transaction.atomic():
                task.save()

        return JsonResponse({'success': True})

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'GET method is not allowed for this action'}, status=405)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = TodoItem
    context_object_name = 'task'
    template_name = 'task_detail.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        task = self.get_object()
        if not task.is_user_allowed(request.user):
            messages.warning(self.request, f'That task does not exist or you are not allowed to see it.')
            return redirect('boards_list')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allowed_group_ids = self.get_object().board.allowed_groups.values_list('id', flat=True)
        assignees = CustomUser.objects.filter(groups__id__in=allowed_group_ids).distinct()
        context['assignees'] = assignees
        return context


class TaskUpdateView(TaskEditorRequiredMixin, UpdateView):
    model = TodoItem

    def set_task_assignee(self, task, task_assignee_data):
        if str(task_assignee_data) == 'unassigned':
            task.assignee = None
        else:
            task_assignee_id = int(task_assignee_data)
            new_assignee = get_object_or_404(CustomUser, id=task_assignee_id)
            task.assignee = new_assignee

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'GET method is not allowed for this action'}, status=405)

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        try:
            body_unicode = request.body.decode("utf-8")
            json_data = json.loads(body_unicode)
            if not task.board.is_archived:
                task_name = json_data.get('taskName')
                task_assignee = json_data.get('taskAssignee')
                self.set_task_assignee(task, task_assignee)

                task_status = json_data.get('taskStatus')
                task_description = json_data.get('taskDescription')

                # Update task data
                if task.name != task_name or task.status != task_status or task.description != task_description:
                    task.name = task_name
                    task.status = task_status
                    task.description = task_description

                    with transaction.atomic():
                        task.save()

                return JsonResponse({'success': True, 'message': 'Task updated successfully.'})
            else:
                messages.warning(self.request, f'You cannot update tasks in archived boards.')
                return JsonResponse({'success': False, 'message': 'Cannot update task.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'})


class TaskDeleteView(TaskEditorRequiredMixin, DeleteView):
    model = TodoItem

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'GET method is not allowed for this action'}, status=405)

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        task_name = task.name
        board_id = task.board.id

        task.delete()
        messages.info(self.request, f'Task {task_name} has been deleted')

        return JsonResponse({'success': True, 'message': f'Task {task_name} has been deleted', 'board_id': board_id})
