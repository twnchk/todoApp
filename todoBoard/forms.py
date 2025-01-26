from django import forms
from django.db.models import Q
from .models import TodoItem, TodoList
from users.models import CustomUser


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = '__all__'

    def __init__(self, *args, init_board_id, user_id, **kwargs):
        if not init_board_id or not user_id:
            raise ValueError("Missing required argument 'init_board_id' or 'user_id'")

        super(CreateTaskForm, self).__init__(*args, **kwargs)

        board = TodoList.objects.get(id=init_board_id)
        allowed_group_ids = set(board.allowed_groups.values_list('id', flat=True))

        self.fields['assignee'].queryset = CustomUser.objects.filter(
            Q(groups__id__in=allowed_group_ids) | Q(is_superuser=True)
        ).distinct()

        self.fields['board'].initial = init_board_id
        self.fields['author'].initial = user_id


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = TodoList
        exclude = ('allowed_groups', 'is_archived',)
