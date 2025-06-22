from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_dashboard, name='department_dashboard'),
    path('add/', views.add_department, name='add_department'),
    path('edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('delete/<int:dept_id>/', views.delete_department, name='delete_department'),
]
