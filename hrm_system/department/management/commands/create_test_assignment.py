from django.core.management.base import BaseCommand
from department.models import Task, Employee, TaskAssignment, Department, Role
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create a test task assignment'

    def handle(self, *args, **options):
        self.stdout.write("Creating test task assignment...")
        
        # Check if we have the necessary data
        tasks = Task.objects.all()
        employees = Employee.objects.all()
        
        self.stdout.write(f"Found {tasks.count()} tasks")
        self.stdout.write(f"Found {employees.count()} employees")
        
        if not tasks.exists():
            self.stdout.write("No tasks found. Creating a test task...")
            # Create a test task
            task = Task.objects.create(
                task_title="Test Task",
                task_description="This is a test task for debugging",
                task_priority="Medium",
                start_date="2024-01-01",
                end_date="2024-12-31",
                task_type="Individual"
            )
            self.stdout.write(f"Created test task: {task}")
        else:
            task = tasks.first()
            self.stdout.write(f"Using existing task: {task}")
        
        if not employees.exists():
            self.stdout.write("No employees found. Creating a test employee...")
            # Create a test department and role
            dept, created = Department.objects.get_or_create(
                dept_name="Test Department",
                defaults={'description': 'Test department for debugging'}
            )
            role, created = Role.objects.get_or_create(
                role_name="Test Role",
                defaults={'description': 'Test role for debugging'}
            )
            
            # Create a test employee
            employee = Employee.objects.create(
                first_name="Test",
                last_name="Employee",
                username="test_employee",
                password="test123",
                email="test@example.com",
                mobile="1234567890",
                date_of_joining="2024-01-01",
                dept=dept,
                role=role
            )
            self.stdout.write(f"Created test employee: {employee}")
        else:
            employee = employees.first()
            self.stdout.write(f"Using existing employee: {employee}")
        
        # Check if assignment already exists
        existing_assignment = TaskAssignment.objects.filter(task=task, employee=employee).first()
        
        if existing_assignment:
            self.stdout.write(f"Assignment already exists: {existing_assignment}")
        else:
            # Create new assignment
            assignment = TaskAssignment.objects.create(
                task=task,
                employee=employee,
                assigned_by=employee,  # For testing, assign to themselves
                status='Pending'
            )
            self.stdout.write(f"Created new assignment: {assignment}")
        
        # Show all assignments
        all_assignments = TaskAssignment.objects.all()
        self.stdout.write(f"Total assignments in database: {all_assignments.count()}")
        
        for assignment in all_assignments:
            self.stdout.write(f"  - {assignment}")
        
        self.stdout.write(self.style.SUCCESS("Test assignment creation completed!")) 