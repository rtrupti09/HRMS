from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_dashboard, name='department_dashboard'),
    path('add/', views.add_department, name='add_department'),
    path('edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('roles/', views.role_dashboard, name='role_dashboard'),
    path('roles/add/', views.add_role, name='add_role'),
    path('roles/edit/<int:role_id>/', views.edit_role, name='edit_role'),
    path('roles/delete/<int:role_id>/', views.delete_role, name='delete_role'),
    path('employees/', views.employee_dashboard, name='employee_dashboard'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('employee-login/', views.employee_login, name='employee_login'),
    path('signup/', views.employee_signup, name='employee_signup'),
    path('logout/', views.employee_logout, name='employee_logout'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/otp/', views.password_reset_otp, name='password_reset_otp'),
    path('password-reset/new/', views.password_reset_new, name='password_reset_new'),
]
