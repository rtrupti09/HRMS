from django.contrib import admin
from .models import Department, Role, Employee

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'dept_name', 'description', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('dept_name', 'description')
    ordering = ('-created_at',)
    list_per_page = 10
    inlines = [RoleInline, EmployeeInline]

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_id', 'role_name', 'description', 'department', 'status', 'created_at', 'updated_at')
    search_fields = ('role_name', 'description')
    list_filter = ('department', 'status', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 10

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id', 'first_name', 'last_name', 'username', 'email', 'mobile',
        'dept', 'role', 'reporting_manager', 'date_of_joining', 'created_at', 'updated_at'
    )
    search_fields = ('first_name', 'last_name', 'username', 'email', 'mobile')
    list_filter = ('dept', 'role', 'date_of_joining', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 10
