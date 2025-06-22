from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'dept_name', 'description', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('dept_name', 'description')
    ordering = ('-created_at',)
    list_per_page = 10
