
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Todo, Teacher
from .forms import TodoForm
from django.core.paginator import Paginator

class TodoDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'todos/todo_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = get_object_or_404(Teacher, user=self.request.user)
        query = self.request.GET.get('q', '')
        all_todos = Todo.objects.filter(teacher=teacher, title__icontains=query).order_by('-created_at')
        paginator = Paginator(all_todos, 5)  # 5 per page
        page = self.request.GET.get('page')
        todos = paginator.get_page(page)
        context['todos'] = todos
        context['query'] = query
        return context

class TodoCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = TodoForm(request.POST)
        teacher = get_object_or_404(Teacher, user=request.user)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.teacher = teacher
            todo.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})

class TodoEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk, teacher__user=request.user)
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})

class TodoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk, teacher__user=request.user)
        todo.delete()
        return JsonResponse({"success": True})

class TodoToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk, teacher__user=request.user)
        todo.is_completed = not todo.is_completed
        todo.save()
        return JsonResponse({"success": True, "completed": todo.is_completed})

class TodoSearchView(LoginRequiredMixin, View):
    def get(self, request):
        teacher = get_object_or_404(Teacher, user=request.user)
        query = request.GET.get('q', '')
        todos = Todo.objects.filter(teacher=teacher, title__icontains=query).values('id', 'title', 'description', 'deadline', 'is_completed')
        return JsonResponse({"results": list(todos)})