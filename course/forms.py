from django import forms
from .models import Session

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['type', 'title', 'topic', 'time']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'time': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'type': 'Session Type',
            'title': 'Session Title',
            'topic': 'Session Topic',
            'time': 'Session Time',
        }   