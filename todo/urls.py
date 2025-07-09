from django.urls import path
from . import views

urlpatterns = [
    path('todos/', views.TodoDashboardView.as_view(), name='todo_dashboard'),
    path('todos/create/', views.TodoCreateView.as_view(), name='todo_create'),
    path('todos/edit/<int:pk>/', views.TodoEditView.as_view(), name='todo_edit'),
    path('todos/delete/<int:pk>/', views.TodoDeleteView.as_view(), name='todo_delete'),
    path('todos/toggle/<int:pk>/', views.TodoToggleView.as_view(), name='todo_toggle'),
]