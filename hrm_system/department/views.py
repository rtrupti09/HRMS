from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Role
from .forms import DepartmentForm, RoleForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

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

@admin_required
def role_dashboard(request):
    roles = Role.objects.filter(status=True)
    query = request.GET.get("search", "")
    if query:
        roles = roles.filter(
            role_name__icontains=query
        ) | roles.filter(
            description__icontains=query
        )
    return render(request, "role/dashboard.html", {"roles": roles, "search": query})

@admin_required
def add_role(request):
    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role added successfully.")
            return redirect('role_dashboard')
    else:
        form = RoleForm()
    return render(request, "role/add_edit.html", {"form": form})

@admin_required
def edit_role(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Role updated successfully.")
            return redirect('role_dashboard')
    else:
        form = RoleForm(instance=role)
    return render(request, "role/add_edit.html", {"form": form})

@admin_required
def delete_role(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    if request.method == "POST":
        role.status = False
        role.save()
        messages.warning(request, "Role deactivated. Users with this role should be reassigned.")
        return redirect('role_dashboard')
    return render(request, "role/confirm_delete.html", {"role": role})

def custom_logout(request):
    logout(request)
    return redirect('/accounts/login/')
