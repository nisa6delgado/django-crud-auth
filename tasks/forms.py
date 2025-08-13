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

        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'important': 'Importante',
        }

        widgets = {
            'title': forms.TextInput(
                attrs={ 'class': 'w-full block p-2 border border-gray-300 rounded mb-5' }
            ),
            'description': forms.Textarea(
                attrs={ 'class': 'w-full block p-2 border border-gray-300 rounded mb-5' }
            ),
            'important': forms.CheckboxInput(
                attrs={ 'class': 'mb-5' }
            ),
        }


class UploadFileForm(forms.Form):
    file = forms.FileField()
    