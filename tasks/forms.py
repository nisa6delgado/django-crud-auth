from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task

        fields = [
            'title',
            'description',
            'important'
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={ 'class': 'w-full block p-2 border border-gray-300 rounded' }
            ),
            'description': forms.Textarea(
                attrs={ 'class': 'w-full block p-2 border border-gray-300 rounded' }
            ),
        }