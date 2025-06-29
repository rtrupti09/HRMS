from django import forms
from .models import Department, Role, Employee, Task, TaskAssignment, PerformanceReview, Leave, LeaveQuota

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'description']

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name', 'description']

    def clean_role_name(self):
        role_name = self.cleaned_data['role_name']
        qs = Role.objects.filter(role_name__iexact=role_name, status=True)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Active role with this name already exists.")
        return role_name

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    date_of_joining = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'username', 'password', 'email', 'mobile',
            'dept', 'role', 'reporting_manager', 'date_of_joining'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dept'].queryset = Department.objects.filter(status=True)
        self.fields['role'].queryset = Role.objects.filter(status=True)
        # Only allow reporting managers with specific roles
        manager_roles = ['Admin', 'Manager', 'Team Leader']
        self.fields['reporting_manager'].queryset = Employee.objects.filter(role__role_name__in=manager_roles)
        self.fields['reporting_manager'].required = False

    def clean(self):
        cleaned_data = super().clean()
        reporting_manager = cleaned_data.get('reporting_manager')
        # Prevent circular reporting
        if self.instance.pk and reporting_manager and reporting_manager.pk == self.instance.pk:
            self.add_error('reporting_manager', 'An employee cannot be their own reporting manager.')
        return cleaned_data

class EmployeeSignupForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        label='Confirm Password'
    )
    date_of_joining = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Date of Joining',
        required=True
    )
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'mobile', 'date_of_joining']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a unique username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Choose a password'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Employee.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

class AdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100, 
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter admin username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter admin password'}), 
        label='Password'
    )

class EmployeeLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}), 
        label='Password'
    )

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='Registered Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        label='OTP',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit OTP', 'maxlength': '6'})
    )

class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}), 
        label='New Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}), 
        label='Confirm Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_title', 'task_description', 'task_priority', 'start_date', 'end_date', 'task_type']
        widgets = {
            'task_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
            'task_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter task description'}),
            'task_priority': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'task_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('End date cannot be earlier than start date.')
        
        return cleaned_data

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ['task', 'employee', 'status']
        widgets = {
            'task': forms.Select(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_superuser:
            # Admin can assign to all employees
            self.fields['employee'].queryset = Employee.objects.all()
        elif user and hasattr(user, 'employee'):
            # Check if this employee is a manager (has team members)
            team_members = Employee.objects.filter(reporting_manager=user.employee)
            if team_members.exists():
                # Manager can assign to their team members
                self.fields['employee'].queryset = team_members
            else:
                # Regular employee can only assign to themselves (for testing)
                self.fields['employee'].queryset = Employee.objects.filter(pk=user.employee.pk)
        else:
            # Fallback to all employees
            self.fields['employee'].queryset = Employee.objects.all()
        
        # Show all tasks that can be assigned
        self.fields['task'].queryset = Task.objects.all()

class TaskFilterForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + TaskAssignment.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_superuser:
            # Admin can see all employees
            self.fields['employee'].queryset = Employee.objects.all()
        elif user and hasattr(user, 'employee'):
            # Check if this employee is a manager (has team members)
            team_members = Employee.objects.filter(reporting_manager=user.employee)
            if team_members.exists():
                # Manager can filter by their team members
                self.fields['employee'].queryset = team_members
            else:
                # Regular employee can only filter by themselves
                self.fields['employee'].queryset = Employee.objects.filter(pk=user.employee.pk)
        else:
            # Fallback to all employees
            self.fields['employee'].queryset = Employee.objects.all()

class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['review_title', 'review_date', 'employee', 'review_period', 'rating', 'comments']
        widgets = {
            'review_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter review title'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'review_period': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'placeholder': 'Rating (1-10)'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter review comments'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_superuser:
            # Admin can review all employees
            self.fields['employee'].queryset = Employee.objects.all()
        elif user and hasattr(user, 'employee'):
            # Check if this employee is a manager (has team members)
            team_members = Employee.objects.filter(reporting_manager=user.employee)
            if team_members.exists():
                # Manager can review their team members
                self.fields['employee'].queryset = team_members
            else:
                # Regular employee can only review themselves (for testing)
                self.fields['employee'].queryset = Employee.objects.filter(pk=user.employee.pk)
        else:
            # Fallback to all employees
            self.fields['employee'].queryset = Employee.objects.all()

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None and (rating < 1 or rating > 10):
            raise forms.ValidationError('Rating must be between 1 and 10')
        return rating

class PerformanceReviewFilterForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        empty_label="All Employees",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    review_period = forms.ChoiceField(
        choices=[('', 'All Periods')] + PerformanceReview.REVIEW_PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser and hasattr(user, 'employee'):
            # For managers, show only their team members
            team_members = Employee.objects.filter(reporting_manager=user.employee)
            if team_members.exists():
                self.fields['employee'].queryset = team_members
            else:
                # If no team members, show only the employee themselves
                self.fields['employee'].queryset = Employee.objects.filter(pk=user.employee.pk)

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'reason', 'start_date', 'end_date']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter reason for leave'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        leave_type = cleaned_data.get('leave_type')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('End date cannot be earlier than start date.')
        
        if start_date and end_date:
            from datetime import date
            if start_date < date.today():
                raise forms.ValidationError('Start date cannot be in the past.')
            
            # Calculate total days
            delta = end_date - start_date
            total_days = delta.days + 1  # Include both start and end date
            cleaned_data['total_days'] = total_days
            
            # Check leave quota if employee is provided and quota exists
            if self.employee and leave_type:
                current_year = date.today().year
                try:
                    quota = LeaveQuota.objects.get(
                        employeeid=self.employee,
                        leave_type=leave_type,
                        year=current_year
                    )
                    if quota.remain_quota < total_days:
                        raise forms.ValidationError(f'Insufficient {leave_type} balance. Available: {quota.remain_quota} days, Requested: {total_days} days.')
                except LeaveQuota.DoesNotExist:
                    # No quota found - allow application but show warning
                    pass  # Don't raise error, just allow the application
        
        return cleaned_data

class LeaveQuotaForm(forms.ModelForm):
    class Meta:
        model = LeaveQuota
        fields = ['employeeid', 'leave_type', 'total_quota', 'year']
        widgets = {
            'employeeid': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'total_quota': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2030'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import date
        current_year = date.today().year
        self.fields['year'].initial = current_year

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employeeid')
        leave_type = cleaned_data.get('leave_type')
        year = cleaned_data.get('year')
        
        if employee and leave_type and year:
            # Check if quota already exists for this employee, leave type, and year
            existing_quota = LeaveQuota.objects.filter(
                employeeid=employee,
                leave_type=leave_type,
                year=year
            )
            if self.instance.pk:
                existing_quota = existing_quota.exclude(pk=self.instance.pk)
            
            if existing_quota.exists():
                raise forms.ValidationError(f'Leave quota for {employee.first_name} {employee.last_name} ({leave_type}) in {year} already exists.')
        
        return cleaned_data

class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove 'pending' from choices for approval form
        self.fields['status'].choices = [choice for choice in Leave.STATUS_CHOICES if choice[0] != 'pending']
