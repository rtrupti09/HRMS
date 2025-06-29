from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Role, Employee, Task, TaskAssignment, PerformanceReview, Leave, LeaveQuota
from .forms import DepartmentForm, RoleForm, EmployeeForm, EmployeeLoginForm, PasswordResetRequestForm, OTPVerificationForm, SetNewPasswordForm, EmployeeSignupForm, AdminLoginForm, TaskForm, TaskAssignmentForm, TaskFilterForm, PerformanceReviewForm, PerformanceReviewFilterForm, LeaveForm, LeaveQuotaForm, LeaveApprovalForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.mail import send_mail
import random
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, date
from django.http import HttpResponse, JsonResponse

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

def is_authenticated_user(request):
    """Check if user is authenticated (either Django user or session-based employee)"""
    return (request.user.is_authenticated or 
            request.session.get('employee_id') is not None)

def get_current_employee(request):
    """Get current employee from either user.employee or session"""
    if hasattr(request.user, 'employee'):
        return request.user.employee
    else:
        employee_id = request.session.get('employee_id')
        if employee_id:
            try:
                return Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return None
    return None

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
    # Check if user was an employee (has employee_id in session)
    if request.session.get('employee_id'):
        request.session.flush()  # Clear all session data
        return redirect('employee_login')
    else:
        # Admin user - redirect to admin login
        return redirect('admin_login')

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
            return render(request, "employee/dashboard.html", {
                "current_employee": current_employee,
                "current_year": date.today().year
            })
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
            employee.password = make_password(form.cleaned_data['password'])
            
            # Set default date_of_joining if not provided
            if not employee.date_of_joining:
                employee.date_of_joining = date.today()
            
            employee.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('employee_login')
    else:
        form = EmployeeSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

# Task Management Views
def task_dashboard(request):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Get filter parameters
    employee_filter = request.GET.get('employee', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Debug information
    print(f"User: {request.user.username}, is_superuser: {request.user.is_superuser}")
    
    # Base queryset for task assignments - Show all assignments for now
    task_assignments = TaskAssignment.objects.all()
    print(f"Total assignments in database: {task_assignments.count()}")
    
    # Apply filters
    if employee_filter:
        task_assignments = task_assignments.filter(employee_id=employee_filter)
        print(f"After employee filter: {task_assignments.count()}")
    
    if status_filter:
        task_assignments = task_assignments.filter(status=status_filter)
        print(f"After status filter: {task_assignments.count()}")
    
    if priority_filter:
        task_assignments = task_assignments.filter(task__task_priority=priority_filter)
        print(f"After priority filter: {task_assignments.count()}")
    
    if start_date:
        task_assignments = task_assignments.filter(task__start_date__gte=start_date)
        print(f"After start date filter: {task_assignments.count()}")
    
    if end_date:
        task_assignments = task_assignments.filter(task__start_date__lte=end_date)
        print(f"After end date filter: {task_assignments.count()}")
    
    # Order by creation date
    task_assignments = task_assignments.order_by('-assigned_date')
    
    # Get unassigned tasks
    assigned_task_ids = task_assignments.values_list('task_id', flat=True)
    unassigned_tasks = Task.objects.exclude(task_id__in=assigned_task_ids)
    
    # Pagination for assigned tasks
    paginator = Paginator(task_assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_tasks = task_assignments.count()
    completed_tasks = task_assignments.filter(status='Completed').count()
    pending_tasks = task_assignments.filter(status='Pending').count()
    in_progress_tasks = task_assignments.filter(status='In Progress').count()
    unassigned_count = unassigned_tasks.count()
    
    print(f"Final statistics - Total: {total_tasks}, Completed: {completed_tasks}, Pending: {pending_tasks}, In Progress: {in_progress_tasks}, Unassigned: {unassigned_count}")
    
    # Get all employees for the dropdown
    employees = Employee.objects.all().order_by('first_name')
    
    context = {
        'page_obj': page_obj,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'unassigned_tasks': unassigned_tasks,
        'unassigned_count': unassigned_count,
        'employees': employees,
    }
    
    return render(request, 'task/dashboard.html', context)

def create_task(request):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task created successfully. You can now assign it to an employee.')
            return redirect('assign_task')
    else:
        form = TaskForm()
    
    return render(request, 'task/add_edit.html', {'form': form, 'action': 'Create'})

def edit_task(request, task_id):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_dashboard')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'task/add_edit.html', {'form': form, 'action': 'Edit', 'task': task})

def delete_task(request, task_id):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_dashboard')
    
    return render(request, 'task/confirm_delete.html', {'task': task})

def assign_task(request):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Get pre-selected task from URL parameter
    pre_selected_task = request.GET.get('task')
    
    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            # Handle both admin and employee users
            current_employee = get_current_employee(request)
            if current_employee:
                assignment.assigned_by = current_employee
            else:
                # For admin users, create a default admin employee record
                from .models import Employee, Role
                try:
                    # Try to get existing admin employee
                    admin_employee = Employee.objects.get(username=request.user.username)
                except Employee.DoesNotExist:
                    # Create a default admin employee record
                    admin_role, created = Role.objects.get_or_create(
                        role_name='Admin',
                        defaults={'description': 'System Administrator'}
                    )
                    admin_employee = Employee.objects.create(
                        first_name=request.user.first_name or 'Admin',
                        last_name=request.user.last_name or 'User',
                        username=request.user.username,
                        email=request.user.email or f'{request.user.username}@admin.com',
                        mobile='N/A',
                        date_of_joining='2024-01-01',
                        role=admin_role
                    )
                assignment.assigned_by = admin_employee
            
            # Debug information
            print(f"Creating assignment: Task={assignment.task}, Employee={assignment.employee}, Assigned by={assignment.assigned_by}")
            
            assignment.save()
            
            # Verify assignment was created
            print(f"Assignment created with ID: {assignment.assignment_id}")
            print(f"Total assignments in database: {TaskAssignment.objects.count()}")
            
            messages.success(request, 'Task assigned successfully.')
            return redirect('task_dashboard')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = TaskAssignmentForm(user=request.user)
        # Pre-select task if provided in URL
        if pre_selected_task:
            try:
                task = Task.objects.get(task_id=pre_selected_task)
                form.fields['task'].initial = task
            except Task.DoesNotExist:
                pass
    
    return render(request, 'task/assign_task.html', {'form': form})

def task_detail(request, assignment_id):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    assignment = get_object_or_404(TaskAssignment, pk=assignment_id)
    
    # Check if user has permission to view this task
    if not request.user.is_superuser:
        current_employee = get_current_employee(request)
        if current_employee:
            if assignment.employee != current_employee and assignment.employee.reporting_manager != current_employee:
                messages.error(request, 'Access denied.')
                return redirect('task_dashboard')
        else:
            messages.error(request, 'Access denied.')
            return redirect('task_dashboard')
    
    return render(request, 'task/detail.html', {'assignment': assignment})

def update_task_status(request, assignment_id):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    assignment = get_object_or_404(TaskAssignment, pk=assignment_id)
    
    # Check if user has permission to update this task
    if not request.user.is_superuser:
        current_employee = get_current_employee(request)
        if current_employee:
            if assignment.employee != current_employee and assignment.employee.reporting_manager != current_employee:
                messages.error(request, 'Access denied.')
                return redirect('task_dashboard')
        else:
            messages.error(request, 'Access denied.')
            return redirect('task_dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        print(f"Updating task status: Assignment ID {assignment_id}, New status: {new_status}")
        
        if new_status in dict(TaskAssignment.STATUS_CHOICES):
            old_status = assignment.status
            assignment.status = new_status
            if new_status == 'Completed':
                assignment.completed_at = datetime.now()
            assignment.save()
            print(f"Status updated successfully: {old_status} -> {new_status}")
            messages.success(request, f'Task status updated from {old_status} to {new_status}.')
        else:
            print(f"Invalid status: {new_status}")
            messages.error(request, f'Invalid status: {new_status}')
    else:
        # Handle GET request - show a simple status update form
        return render(request, 'task/update_status.html', {
            'assignment': assignment,
            'status_choices': TaskAssignment.STATUS_CHOICES
        })
    
    # Redirect back to the appropriate dashboard
    if request.user.is_superuser:
        return redirect('task_dashboard')
    else:
        return redirect('employee_task_dashboard')

def employee_task_dashboard(request):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Get current employee
    employee = get_current_employee(request)
    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_login')
    
    # Get tasks assigned to the current employee
    task_assignments = TaskAssignment.objects.filter(employee=employee)
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    if status_filter:
        task_assignments = task_assignments.filter(status=status_filter)
    
    if priority_filter:
        task_assignments = task_assignments.filter(task__task_priority=priority_filter)
    
    # Order by assigned date
    task_assignments = task_assignments.order_by('-assigned_date')
    
    # Pagination
    paginator = Paginator(task_assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_tasks = task_assignments.count()
    completed_tasks = task_assignments.filter(status='Completed').count()
    pending_tasks = task_assignments.filter(status='Pending').count()
    in_progress_tasks = task_assignments.filter(status='In Progress').count()
    
    context = {
        'page_obj': page_obj,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'current_employee': employee,
    }
    
    return render(request, 'task/employee_dashboard.html', context)

def debug_task_assignments(request):
    """Debug view to check task assignments"""
    if not request.user.is_superuser:
        return HttpResponse("Access denied", status=403)
    
    debug_info = {
        'total_tasks': Task.objects.count(),
        'total_employees': Employee.objects.count(),
        'total_assignments': TaskAssignment.objects.count(),
        'assignments': [
            {
                'id': a.assignment_id,
                'task': a.task.task_title,
                'employee': f"{a.employee.first_name} {a.employee.last_name}",
                'status': a.status,
                'assigned_date': a.assigned_date.isoformat() if a.assigned_date else None,
            }
            for a in TaskAssignment.objects.all()[:10]
        ],
        'tasks': [
            {
                'id': t.task_id,
                'title': t.task_title,
                'priority': t.task_priority,
            }
            for t in Task.objects.all()[:5]
        ],
        'employees': [
            {
                'id': e.employee_id,
                'name': f"{e.first_name} {e.last_name}",
                'username': e.username,
            }
            for e in Employee.objects.all()[:5]
        ],
    }
    
    return JsonResponse(debug_info)

# Performance Review Views
def review_dashboard(request):
    """Dashboard for viewing performance reviews"""
    if request.user.is_authenticated and request.user.is_superuser:
        # Admin view - show all reviews
        reviews = PerformanceReview.objects.all().order_by('-review_date')
    else:
        # Employee view - show only reviews for current employee
        employee_id = request.session.get('employee_id')
        if employee_id:
            current_employee = Employee.objects.get(employee_id=employee_id)
            reviews = PerformanceReview.objects.filter(employee=current_employee).order_by('-review_date')
        else:
            messages.error(request, 'Please login first.')
            return redirect('employee_login')
    
    # Apply filters
    filter_form = PerformanceReviewFilterForm(request.GET, user=request.user)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('employee'):
            reviews = reviews.filter(employee=filter_form.cleaned_data['employee'])
        if filter_form.cleaned_data.get('review_period'):
            reviews = reviews.filter(review_period=filter_form.cleaned_data['review_period'])
        if filter_form.cleaned_data.get('start_date'):
            reviews = reviews.filter(review_date__gte=filter_form.cleaned_data['start_date'])
        if filter_form.cleaned_data.get('end_date'):
            reviews = reviews.filter(review_date__lte=filter_form.cleaned_data['end_date'])
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_reviews': reviews.count(),
    }
    
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, "review/admin_dashboard.html", context)
    else:
        return render(request, "review/employee_dashboard.html", context)

@admin_only
def create_review(request):
    """Create a new performance review (Admin/Manager/TL only)"""
    if request.method == "POST":
        form = PerformanceReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            # Set the reviewer as the current user
            if hasattr(request.user, 'employee'):
                review.reviewed_by = request.user.employee
            else:
                # For admin users, we need to handle this differently
                # For now, we'll use the first employee as reviewer (you can modify this)
                review.reviewed_by = Employee.objects.first()
            review.save()
            messages.success(request, "Performance review created successfully.")
            return redirect('review_dashboard')
    else:
        form = PerformanceReviewForm(user=request.user)
    
    return render(request, "review/add_edit.html", {"form": form, "title": "Add Performance Review"})

@admin_only
def edit_review(request, review_id):
    """Edit an existing performance review"""
    review = get_object_or_404(PerformanceReview, pk=review_id)
    if request.method == "POST":
        form = PerformanceReviewForm(request.POST, instance=review, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Performance review updated successfully.")
            return redirect('review_dashboard')
    else:
        form = PerformanceReviewForm(instance=review, user=request.user)
    
    return render(request, "review/add_edit.html", {"form": form, "title": "Edit Performance Review"})

@admin_only
def delete_review(request, review_id):
    """Delete a performance review"""
    review = get_object_or_404(PerformanceReview, pk=review_id)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Performance review deleted successfully.")
        return redirect('review_dashboard')
    return render(request, "review/confirm_delete.html", {"review": review})

def review_detail(request, review_id):
    """View details of a performance review"""
    review = get_object_or_404(PerformanceReview, pk=review_id)
    
    # Check if user has permission to view this review
    if request.user.is_authenticated and request.user.is_superuser:
        # Admin can view all reviews
        pass
    else:
        # Employee can only view their own reviews
        employee_id = request.session.get('employee_id')
        if not employee_id or review.employee.employee_id != int(employee_id):
            messages.error(request, 'Access denied.')
            return redirect('review_dashboard')
    
    return render(request, "review/detail.html", {"review": review})

def manager_review_dashboard(request):
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    current_employee = get_current_employee(request)
    if not current_employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_login')
    
    # Get team members (employees who report to this manager)
    team_members = Employee.objects.filter(reporting_manager=current_employee)
    
    if not team_members.exists():
        messages.warning(request, 'You have no team members to review.')
        return redirect('review_dashboard')
    
    # Get reviews for team members
    reviews = PerformanceReview.objects.filter(employee__in=team_members).order_by('-review_date')
    
    # Apply filters
    form = PerformanceReviewFilterForm(request.GET, user=request.user)
    if form.is_valid():
        employee = form.cleaned_data.get('employee')
        review_period = form.cleaned_data.get('review_period')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if employee:
            reviews = reviews.filter(employee=employee)
        if review_period:
            reviews = reviews.filter(review_period=review_period)
        if start_date:
            reviews = reviews.filter(review_date__gte=start_date)
        if end_date:
            reviews = reviews.filter(review_date__lte=end_date)
    
    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'team_members': team_members,
    }
    
    return render(request, 'review/manager_dashboard.html', context)

# Leave Management Views

def employee_leave_dashboard(request):
    """Employee leave dashboard showing their leave balance and history"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    current_employee = get_current_employee(request)
    if not current_employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_login')
    
    # Get leave balance for current year
    current_year = date.today().year
    leave_quotas = LeaveQuota.objects.filter(employeeid=current_employee, year=current_year)
    
    # Get leave history
    leaves = Leave.objects.filter(employeeid=current_employee).order_by('-created_at')
    
    # Pagination for leave history
    paginator = Paginator(leaves, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'current_employee': current_employee,
        'leave_quotas': leave_quotas,
        'page_obj': page_obj,
        'current_year': current_year,
    }
    
    return render(request, 'leave/employee_dashboard.html', context)

def apply_leave(request):
    """Employee applies for leave"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    current_employee = get_current_employee(request)
    if not current_employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_login')
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, employee=current_employee)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employeeid = current_employee
            
            # Calculate total days
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            delta = end_date - start_date
            leave.total_days = delta.days + 1  # Include both start and end date
            
            leave.save()
            messages.success(request, 'Leave application submitted successfully.')
            return redirect('employee_leave_dashboard')
    else:
        form = LeaveForm(employee=current_employee)
    
    context = {
        'form': form,
        'current_employee': current_employee,
        'current_year': date.today().year,
    }
    
    return render(request, 'leave/apply_leave.html', context)

def edit_leave(request, leave_id):
    """Employee edits their leave application (only if pending)"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    current_employee = get_current_employee(request)
    if not current_employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_login')
    
    leave = get_object_or_404(Leave, leaveid=leave_id, employeeid=current_employee)
    
    # Check if leave can be edited (only if pending)
    if leave.status != 'pending':
        messages.error(request, 'Leave cannot be edited once approved or rejected.')
        return redirect('employee_leave_dashboard')
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave, employee=current_employee)
        if form.is_valid():
            leave = form.save(commit=False)
            
            # Calculate total days
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            delta = end_date - start_date
            leave.total_days = delta.days + 1  # Include both start and end date
            
            leave.save()
            messages.success(request, 'Leave application updated successfully.')
            return redirect('employee_leave_dashboard')
    else:
        form = LeaveForm(instance=leave, employee=current_employee)
    
    context = {
        'form': form,
        'leave': leave,
        'current_employee': current_employee,
    }
    
    return render(request, 'leave/edit_leave.html', context)

def admin_leave_dashboard(request):
    """Admin/Manager leave dashboard for approving leaves"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Check if user is admin or manager
    is_admin = request.user.is_superuser
    current_employee = get_current_employee(request)
    
    if is_admin:
        # Admin can see all leaves
        pending_leaves = Leave.objects.filter(status='pending').order_by('-created_at')
        all_leaves = Leave.objects.all().order_by('-created_at')
        current_employee = None  # Admin doesn't need employee context
    elif current_employee:
        # Check if employee is manager
        is_manager = current_employee.role and current_employee.role.role_name.lower() in ['manager', 'team leader', 'hr']
        
        if not is_manager:
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('employee_leave_dashboard')
        
        # Manager can see leaves from their team members
        team_members = Employee.objects.filter(reporting_manager=current_employee)
        pending_leaves = Leave.objects.filter(employeeid__in=team_members, status='pending').order_by('-created_at')
        all_leaves = Leave.objects.filter(employeeid__in=team_members).order_by('-created_at')
    else:
        messages.error(request, 'Access denied. Admin or Manager privileges required.')
        return redirect('employee_login')
    
    # Pagination
    paginator = Paginator(pending_leaves, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_leaves': pending_leaves,
        'all_leaves': all_leaves,
        'page_obj': page_obj,
        'current_employee': current_employee,
        'is_admin': is_admin,
    }
    
    return render(request, 'leave/admin_dashboard.html', context)

def approve_leave(request, leave_id):
    """Manager/Admin approves or rejects leave"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Check if user is admin or manager
    is_admin = request.user.is_superuser
    current_employee = get_current_employee(request)
    
    if is_admin:
        # Admin can approve any leave
        leave = get_object_or_404(Leave, leaveid=leave_id)
        current_employee = None  # Admin doesn't need employee context
    elif current_employee:
        # Check if employee is manager
        is_manager = current_employee.role and current_employee.role.role_name.lower() in ['manager', 'team leader', 'hr']
        
        if not is_manager:
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('employee_leave_dashboard')
        
        leave = get_object_or_404(Leave, leaveid=leave_id)
        
        # Check if manager can approve this leave
        if leave.employeeid.reporting_manager != current_employee:
            messages.error(request, 'You can only approve leaves from your team members.')
            return redirect('admin_leave_dashboard')
    else:
        messages.error(request, 'Access denied. Admin or Manager privileges required.')
        return redirect('employee_login')
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save(commit=False)
            # For admin, we'll set approved_by to None or create a system approval
            if current_employee:
                leave.approved_by = current_employee
            else:
                # For admin, we'll leave approved_by as None or set to a system user
                leave.approved_by = None
            leave.save()
            
            # Update leave quota if approved
            if leave.status == 'approved':
                try:
                    quota = LeaveQuota.objects.get(
                        employeeid=leave.employeeid,
                        leave_type=leave.leave_type,
                        year=date.today().year
                    )
                    quota.used_quota += leave.total_days
                    quota.save()
                except LeaveQuota.DoesNotExist:
                    messages.warning(request, 'Leave approved but quota not found. Please contact HR.')
            
            messages.success(request, f'Leave {leave.status} successfully.')
            return redirect('admin_leave_dashboard')
    else:
        form = LeaveApprovalForm(instance=leave)
    
    context = {
        'form': form,
        'leave': leave,
        'current_employee': current_employee,
    }
    
    return render(request, 'leave/approve_leave.html', context)

def leave_quota_dashboard(request):
    """HR/Admin dashboard for managing leave quotas"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Check if user is admin or HR
    is_admin = request.user.is_superuser
    current_employee = get_current_employee(request)
    
    if is_admin:
        # Admin can manage all quotas
        quotas = LeaveQuota.objects.all().order_by('-year', 'employeeid__first_name')
        current_employee = None  # Admin doesn't need employee context
    elif current_employee:
        # Check if employee is HR
        is_hr = current_employee.role and current_employee.role.role_name.lower() == 'hr'
        
        if not is_hr:
            messages.error(request, 'Access denied. HR privileges required.')
            return redirect('employee_leave_dashboard')
        
        # HR can manage all quotas
        quotas = LeaveQuota.objects.all().order_by('-year', 'employeeid__first_name')
    else:
        messages.error(request, 'Access denied. Admin or HR privileges required.')
        return redirect('employee_login')
    
    # Pagination
    paginator = Paginator(quotas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_employee': current_employee,
    }
    
    return render(request, 'leave/quota_dashboard.html', context)

def add_leave_quota(request):
    """Add new leave quota"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Check if user is admin or HR
    is_admin = request.user.is_superuser
    current_employee = get_current_employee(request)
    
    if is_admin:
        # Admin can add quotas
        current_employee = None  # Admin doesn't need employee context
    elif current_employee:
        # Check if employee is HR
        is_hr = current_employee.role and current_employee.role.role_name.lower() == 'hr'
        
        if not is_hr:
            messages.error(request, 'Access denied. HR privileges required.')
            return redirect('employee_leave_dashboard')
    else:
        messages.error(request, 'Access denied. Admin or HR privileges required.')
        return redirect('employee_login')
    
    if request.method == 'POST':
        form = LeaveQuotaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave quota added successfully.')
            return redirect('leave_quota_dashboard')
    else:
        form = LeaveQuotaForm()
    
    context = {
        'form': form,
        'current_employee': current_employee,
    }
    
    return render(request, 'leave/add_quota.html', context)

def edit_leave_quota(request, quota_id):
    """Edit existing leave quota"""
    if not is_authenticated_user(request):
        messages.error(request, 'Please login first.')
        return redirect('employee_login')
    
    # Check if user is admin or HR
    is_admin = request.user.is_superuser
    current_employee = get_current_employee(request)
    
    if is_admin:
        # Admin can edit any quota
        quota = get_object_or_404(LeaveQuota, quotaid=quota_id)
        current_employee = None  # Admin doesn't need employee context
    elif current_employee:
        # Check if employee is HR
        is_hr = current_employee.role and current_employee.role.role_name.lower() == 'hr'
        
        if not is_hr:
            messages.error(request, 'Access denied. HR privileges required.')
            return redirect('employee_leave_dashboard')
        
        quota = get_object_or_404(LeaveQuota, quotaid=quota_id)
    else:
        messages.error(request, 'Access denied. Admin or HR privileges required.')
        return redirect('employee_login')
    
    if request.method == 'POST':
        form = LeaveQuotaForm(request.POST, instance=quota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave quota updated successfully.')
            return redirect('leave_quota_dashboard')
    else:
        form = LeaveQuotaForm(instance=quota)
    
    context = {
        'form': form,
        'quota': quota,
        'current_employee': current_employee,
    }
    
    return render(request, 'leave/edit_quota.html', context)
