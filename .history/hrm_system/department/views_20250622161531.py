# department/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Department
from .forms import DepartmentForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@admin_required
def department_dashboard(request):
    departments = Department.objects.filter(status=True)
    query = request.GET.get("search", "")
    if query:
        departments = departments.filter(
            dept_name__icontains=query
        ) | departments.filter(
            description__icontains=query
        )
    return render(request, "department/dashboard.html", {"departments": departments, "search": query})

@admin_required
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully.")
            return redirect('department_dashboard')
    else:
        form = DepartmentForm()
    return render(request, "department/add_edit.html", {"form": form})

@admin_required
def edit_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect('department_dashboard')
    else:
        form = DepartmentForm(instance=department)
    return render(request, "department/add_edit.html", {"form": form})

@admin_required
def delete_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if request.method == "POST":
        department.status = False  
        department.save()
        messages.warning(request, "Department deactivated. Reassign employees before deletion.")
        return redirect('department_dashboard')
    return render(request, "department/confirm_delete.html", {"department": department})
