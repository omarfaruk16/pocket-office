from django.shortcuts import render, redirect
from .forms import TeacherForm,  TeacherLoginForm, DegreeForm
from .models import Teacher, Degree
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TeacherRegistrationForm

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            Teacher.objects.create(
                user=user,
                teacher_id=form.cleaned_data['teacher_id'],
                phone=form.cleaned_data['phone'],
                permanent_address=form.cleaned_data['permanent_address'],
                picture=form.cleaned_data['picture']
            )
            return redirect('teacher_login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'teacher_register.html', {'form': form})


def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'teacher_list.html', {'teachers': teachers})

class TeacherLoginView(View):
    template_name = 'teacher_login.html'
    
    def get(self, request):
        form = TeacherLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('teacher_profile')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email.')

        return render(request, self.template_name, {'form': form})

class TeacherLogOutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('teacher_login')
    
class TeacherProfileView(LoginRequiredMixin, View):
    template_name = 'teacher_profile.html'

    def get(self, request, *args, **kwargs):
        # Fetch the current user's teacher profile
        try:
            teacher_profile = request.user.teacher  # Assumes User has related Teacher via OneToOneField
        except Teacher.DoesNotExist:
            teacher_profile = None

        context = {
            'teacher': teacher_profile,
        }

        return render(request, self.template_name, context)
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Degree
from .forms import DegreeForm

@login_required
def degree_list_view(request):
    teacher = request.user.teacher
    degrees = Degree.objects.filter(teacher=teacher)
    form = DegreeForm()
    return render(request, 'degree_list.html', {'degrees': degrees, 'form': form})

@login_required
def degree_create_view(request):
    if request.method == 'POST':
        form = DegreeForm(request.POST)
        if form.is_valid():
            degree = form.save(commit=False)
            degree.teacher = request.user.teacher
            degree.save()
    return redirect('degree_list')

@login_required
def degree_edit_view(request, pk):
    degree = get_object_or_404(Degree, pk=pk, teacher=request.user.teacher)
    if request.method == 'POST':
        form = DegreeForm(request.POST, instance=degree)
        if form.is_valid():
            form.save()
            return redirect('degree_list')
    else:
        form = DegreeForm(instance=degree)
    return render(request, 'edit_degree.html', {'form': form, 'degree': degree})

@login_required
def degree_delete_view(request, pk):
    degree = get_object_or_404(Degree, pk=pk, teacher=request.user.teacher)
    degree.delete()
    return redirect('degree_list')
