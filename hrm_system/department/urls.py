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
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/otp/', views.password_reset_otp, name='password_reset_otp'),
    path('password-reset/new/', views.password_reset_new, name='password_reset_new'),
    
    # Task Management URLs
    path('tasks/', views.task_dashboard, name='task_dashboard'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/assign/', views.assign_task, name='assign_task'),
    path('tasks/detail/<int:assignment_id>/', views.task_detail, name='task_detail'),
    path('tasks/update-status/<int:assignment_id>/', views.update_task_status, name='update_task_status'),
    path('tasks/employee/', views.employee_task_dashboard, name='employee_task_dashboard'),
    path('debug/task-assignments/', views.debug_task_assignments, name='debug_task_assignments'),
    
    # Performance Review URLs
    path('reviews/', views.review_dashboard, name='review_dashboard'),
    path('reviews/create/', views.create_review, name='create_review'),
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('reviews/detail/<int:review_id>/', views.review_detail, name='review_detail'),
    path('reviews/manager/', views.manager_review_dashboard, name='manager_review_dashboard'),
    
    # Leave Management URLs
    path('leaves/', views.employee_leave_dashboard, name='employee_leave_dashboard'),
    path('leaves/apply/', views.apply_leave, name='apply_leave'),
    path('leaves/edit/<int:leave_id>/', views.edit_leave, name='edit_leave'),
    path('leaves/admin/', views.admin_leave_dashboard, name='admin_leave_dashboard'),
    path('leaves/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leaves/quota/', views.leave_quota_dashboard, name='leave_quota_dashboard'),
    path('leaves/quota/add/', views.add_leave_quota, name='add_leave_quota'),
    path('leaves/quota/edit/<int:quota_id>/', views.edit_leave_quota, name='edit_leave_quota'),
]
