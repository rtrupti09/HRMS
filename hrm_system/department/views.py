from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Role, Employee
from .forms import DepartmentForm, RoleForm, EmployeeForm, EmployeeLoginForm, PasswordResetRequestForm, OTPVerificationForm, SetNewPasswordForm, EmployeeSignupForm, AdminLoginForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.mail import send_mail
import random
from django.contrib.auth.models import User

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def is_admin_user(request):
    return request.user.is_authenticated and request.user.is_superuser

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin_user(request):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('employee_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_only
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

@admin_only
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

@admin_only
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

@admin_only
def delete_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if request.method == "POST":
        department.status = False  
        department.save()
        messages.warning(request, "Department deactivated. Reassign employees before deletion.")
        return redirect('department_dashboard')
    return render(request, "department/confirm_delete.html", {"department": department})

@admin_only
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

@admin_only
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

@admin_only
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

@admin_only
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

def is_admin_or_hr(user):
    return user.is_superuser or (hasattr(user, 'employee') and user.employee.role and user.employee.role.role_name.lower() == 'hr')

employee_required = user_passes_test(is_admin_or_hr)

def employee_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        # Admin view - show all employees
        employees = Employee.objects.all()
        query = request.GET.get("search", "")
        if query:
            employees = employees.filter(
                first_name__icontains=query
            ) | employees.filter(
                last_name__icontains=query
            ) | employees.filter(
                username__icontains=query
            )
        return render(request, "employee/dashboard.html", {"employees": employees, "search": query})
    else:
        # Employee view - show only current employee
        employee_id = request.session.get('employee_id')
        if employee_id:
            current_employee = Employee.objects.get(employee_id=employee_id)
            return render(request, "employee/dashboard.html", {"current_employee": current_employee})
        else:
            messages.error(request, 'Please login first.')
            return redirect('employee_login')

@admin_only
def add_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            # Hash password securely
            if form.cleaned_data['password']:
                employee.password = make_password(form.cleaned_data['password'])
            employee.save()
            messages.success(request, "Employee added successfully.")
            return redirect('department_dashboard')
    else:
        form = EmployeeForm()
    return render(request, "employee/add_edit.html", {"form": form})

@employee_required
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect('employee_dashboard')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "employee/add_edit.html", {"form": form, "employee": employee})

@employee_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == "POST":
        employee.delete()
        messages.warning(request, "Employee deleted.")
        return redirect('employee_dashboard')
    return render(request, "employee/confirm_delete.html", {"employee": employee})

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                request.session['is_admin'] = True
                return redirect('department_dashboard')
            else:
                messages.error(request, 'Invalid username or password or insufficient privileges.')
    else:
        form = AdminLoginForm()
    return render(request, 'registration/admin_login.html', {'form': form})

def employee_login(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                employee = Employee.objects.get(email=email)
                if check_password(password, employee.password):
                    request.session['employee_id'] = employee.employee_id
                    request.session['is_admin'] = False
                    return redirect('employee_dashboard')
                else:
                    messages.error(request, 'Invalid email or password.')
            except Employee.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = EmployeeLoginForm()
    return render(request, 'registration/employee_login.html', {'form': form})

def employee_logout(request):
    request.session.flush()
    return redirect('employee_login')

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                employee = Employee.objects.get(email=email)
                otp = str(random.randint(100000, 999999))
                request.session['reset_email'] = email
                request.session['reset_otp'] = otp
                send_mail(
                    'Your Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return redirect('password_reset_otp')
            except Employee.DoesNotExist:
                messages.error(request, 'No employee found with this email.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'registration/password_reset_request.html', {'form': form})

def password_reset_otp(request):
    if 'reset_email' not in request.session:
        return redirect('password_reset_request')
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == request.session.get('reset_otp'):
                request.session['otp_verified'] = True
                return redirect('password_reset_new')
            else:
                messages.error(request, 'Invalid OTP.')
    else:
        form = OTPVerificationForm()
    return render(request, 'registration/password_reset_otp.html', {'form': form})

def password_reset_new(request):
    if not request.session.get('otp_verified'):
        return redirect('password_reset_request')
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            email = request.session.get('reset_email')
            new_password = form.cleaned_data['new_password']
            try:
                employee = Employee.objects.get(email=email)
                employee.password = make_password(new_password)
                employee.save()
                # Clear session
                for key in ['reset_email', 'reset_otp', 'otp_verified']:
                    if key in request.session:
                        del request.session[key]
                messages.success(request, 'Password reset successful. Please login with your new password.')
                return redirect('employee_login')
            except Employee.DoesNotExist:
                messages.error(request, 'Unexpected error. Please try again.')
    else:
        form = SetNewPasswordForm()
    return render(request, 'registration/password_reset_new.html', {'form': form})

def employee_signup(request):
    if request.method == 'POST':
        form = EmployeeSignupForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            # Hash the password
            employee.password = make_password(form.cleaned_data['password'])
            # Set default values for required fields
            employee.mobile = 'N/A'
            employee.date_of_joining = '2024-01-01'
            employee.save()
            messages.success(request, 'Registration successful! Please login with your email and password.')
            return redirect('employee_login')
    else:
        form = EmployeeSignupForm()
    return render(request, 'registration/signup.html', {'form': form})
