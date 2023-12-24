from django import forms
from .models import TodoItem, TodoList


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = '__all__'
        ''' TODO: remove 'author' field after users functionality is added,
                  change to predefined value for currently logged user '''

    def __init__(self, *args, init_board_id, user_id, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)

        # set initial board_id field
        self.fields['category'].initial = init_board_id
        self.fields['author'].initial = user_id
        # self.fields['category'].widget.attrs['disabled'] = True


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = '__all__'
