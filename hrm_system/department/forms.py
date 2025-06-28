from django import forms
from .models import Department, Role, Employee

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
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a unique username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Choose a password'}),
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
