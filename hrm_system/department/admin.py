from django.contrib import admin
from .models import Department, Role, Employee, Task, TaskAssignment, PerformanceReview, Leave, LeaveQuota

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1

class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 1
    readonly_fields = ('assigned_date', 'completed_at')

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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_title', 'task_priority', 'task_type', 'start_date', 'end_date', 'created_at')
    search_fields = ('task_title', 'task_description')
    list_filter = ('task_priority', 'task_type', 'start_date', 'end_date', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 10
    inlines = [TaskAssignmentInline]

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment_id', 'task', 'employee', 'assigned_by', 'status', 'assigned_date', 'completed_at')
    search_fields = ('task__task_title', 'employee__first_name', 'employee__last_name')
    list_filter = ('status', 'assigned_date', 'completed_at', 'task__task_priority')
    ordering = ('-assigned_date',)
    list_per_page = 10
    readonly_fields = ('assigned_date', 'completed_at')

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'review_title', 'employee', 'reviewed_by', 'review_period', 'rating', 'review_date', 'created_at')
    search_fields = ('review_title', 'employee__first_name', 'employee__last_name', 'reviewed_by__first_name', 'reviewed_by__last_name')
    list_filter = ('review_period', 'rating', 'review_date', 'created_at', 'employee__dept')
    ordering = ('-review_date',)
    list_per_page = 10
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('review_title', 'review_date', 'review_period', 'rating', 'comments')
        }),
        ('Employee Information', {
            'fields': ('employee', 'reviewed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'reviewed_by', 'employee__dept', 'reviewed_by__dept')

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employeeid', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'created_at')
    list_filter = ('leave_type', 'status', 'start_date', 'end_date', 'created_at')
    search_fields = ('employeeid__first_name', 'employeeid__last_name', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('total_days',)

@admin.register(LeaveQuota)
class LeaveQuotaAdmin(admin.ModelAdmin):
    list_display = ('employeeid', 'leave_type', 'year', 'total_quota', 'used_quota', 'remain_quota')
    list_filter = ('leave_type', 'year', 'employeeid__dept')
    search_fields = ('employeeid__first_name', 'employeeid__last_name')
    ordering = ('-year', 'employeeid__first_name')
    readonly_fields = ('remain_quota',)
