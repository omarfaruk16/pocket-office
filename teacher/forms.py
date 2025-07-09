from django import forms
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Teacher
from .models import Degree

class TeacherRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    teacher_id = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Teacher's ID"}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Email'}))
    phone = forms.CharField(max_length=13, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Mobile Number'}))
    permanent_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Address'}))
    picture = forms.ImageField()

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()

        # Password match check
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")

        # Email uniqueness check
        email = cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "This email is already in use.")

        return cleaned_data
# Degree formset
class DegreeForm(forms.ModelForm):
    class Meta:
        model = Degree
        fields = ['degree_name', 'slug', 'university', 'passing_year', 'result']
        widgets = {
            'degree_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control'}),
            'passing_year': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'result': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Teacher form
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'picture']


# Login form
class TeacherLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
