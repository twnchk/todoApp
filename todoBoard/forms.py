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

        self.fields['assignee'].queryset = CustomUser.objects.filter(
            Q(allowed_boards=board) | Q(pk=board.owner.pk)
        ).distinct()

        self.fields['board'].initial = init_board_id
        self.fields['author'].initial = user_id


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = TodoList
        exclude = ('is_archived','owner',)
