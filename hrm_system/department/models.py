# models.py for department app
# Add your Department and Role models here 
from django.db import models

class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    dept_name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.dept_name

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles', null=True, blank=True)

    def __str__(self):
        return self.role_name

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    mobile = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dept = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    role = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)
    reporting_manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team'),
    ]
    
    task_id = models.AutoField(primary_key=True)
    task_title = models.CharField(max_length=100)
    task_description = models.CharField(max_length=300)
    task_priority = models.CharField(max_length=200, choices=PRIORITY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_title

class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    assignment_id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='task_assignments')
    assigned_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task.task_title} - {self.employee.first_name} {self.employee.last_name}"

class PerformanceReview(models.Model):
    REVIEW_PERIOD_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Annual', 'Annual'),
    ]
    
    review_id = models.AutoField(primary_key=True)
    review_title = models.CharField(max_length=100)
    review_date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews_received')
    reviewed_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews_given')
    review_period = models.CharField(max_length=100, choices=REVIEW_PERIOD_CHOICES)
    rating = models.IntegerField()
    comments = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.review_title} - {self.employee.first_name} {self.employee.last_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rating < 1 or self.rating > 10:
            raise ValidationError('Rating must be between 1 and 10')

class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('SL', 'Sick Leave'),
        ('CL', 'Casual Leave'),
        ('PL', 'Privilege Leave'),
        ('LWP', 'Leave Without Pay'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    leaveid = models.AutoField(primary_key=True)
    employeeid = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPE_CHOICES)
    reason = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employeeid.first_name} {self.employeeid.last_name} - {self.leave_type} ({self.start_date} to {self.end_date})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('End date cannot be earlier than start date.')

class LeaveQuota(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('SL', 'Sick Leave'),
        ('CL', 'Casual Leave'),
        ('PL', 'Privilege Leave'),
        ('LWP', 'Leave Without Pay'),
    ]
    
    quotaid = models.AutoField(primary_key=True)
    employeeid = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_quotas')
    leave_type = models.CharField(max_length=3, choices=LEAVE_TYPE_CHOICES)
    total_quota = models.IntegerField()
    used_quota = models.IntegerField(default=0)
    remain_quota = models.IntegerField()
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employeeid', 'leave_type', 'year']

    def __str__(self):
        return f"{self.employeeid.first_name} {self.employeeid.last_name} - {self.leave_type} ({self.year})"

    def save(self, *args, **kwargs):
        self.remain_quota = self.total_quota - self.used_quota
        super().save(*args, **kwargs) 