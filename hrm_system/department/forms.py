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
