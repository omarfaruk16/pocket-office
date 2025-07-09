from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.teacher_register, name='teacher_register'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('login/', views.TeacherLoginView.as_view(), name='teacher_login'),
    path('logout/', views.TeacherLogOutView.as_view(), name='teacher_logout'),
    path('profile/', views.TeacherProfileView.as_view(), name='teacher_profile'),
    path('degrees/', views.degree_list_view, name='degree_list'),
    path('degrees/create/', views.degree_create_view, name='degree_create'),
    path('degrees/<int:pk>/edit/', views.degree_edit_view, name='degree_edit'),
    path('degrees/<int:pk>/delete/', views.degree_delete_view, name='degree_delete'),
]
