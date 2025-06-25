from django import forms
from .models import Department, Role

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
