from django.urls import path
from . import views

urlpatterns = [
    # Teacher Dashboard
    path('teacher/dashboard/', views.TeacherPartListView.as_view(), name='teacher_part_list'),

    # Combined Sessions
    path('part/<int:part_id>/sessions/', views.all_sessions_combined, name='all_sessions_combined'),

    # Performance Charts
    #path('part/<int:part_id>/charts/', views.performance_chart, name='performance_chart'),
    #path('part/<int:part_id>/student/<int:student_id>/chart/', views.student_performance_chart, name='student_performance_chart'),

    # Class Session
    path('part/<int:part_id>/class/create/', views.class_session_create, name='class_session_create'),
    path('class/<int:session_id>/edit/', views.class_session_edit, name='class_session_edit'),
    path('class/<int:session_id>/delete/', views.class_session_delete, name='class_session_delete'),

    # Class Test
    path('part/<int:part_id>/ct/create/', views.class_test_create, name='class_test_create'),
    path('ct/<int:test_id>/edit/', views.class_test_edit, name='class_test_edit'),
    path('ct/<int:test_id>/delete/', views.class_test_delete, name='class_test_delete'),

    # Exam
    path('part/<int:part_id>/exam/create/', views.exam_create, name='exam_create'),
    path('exam/<int:exam_id>/edit/', views.exam_edit, name='exam_edit'),
    path('exam/<int:exam_id>/delete/', views.exam_delete, name='exam_delete'),

    # Student Summary
    path('part/<int:part_id>/student/<int:student_id>/summary/', views.student_result_summary, name='student_result_summary'),
]
