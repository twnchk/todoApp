from django import forms
from .models import TodoItem, TodoList


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = '__all__'

    def __init__(self, *args, init_board_id, user_id, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        self.fields['board'].initial = init_board_id
        self.fields['author'].initial = user_id


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = TodoList
        exclude = ('allowed_groups',)
