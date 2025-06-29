from django.core.management.base import BaseCommand
from department.models import Task, Employee, TaskAssignment, Department, Role
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test task assignment creation and display'

    def handle(self, *args, **options):
        self.stdout.write("Testing task assignment system...")
        
        # Check if we have the necessary data
        tasks = Task.objects.all()
        employees = Employee.objects.all()
        
        self.stdout.write(f"Found {tasks.count()} tasks")
        self.stdout.write(f"Found {employees.count()} employees")
        
        if tasks.exists() and employees.exists():
            # Create a test assignment
            task = tasks.first()
            employee = employees.first()
            
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
        else:
            self.stdout.write("No tasks or employees found. Please create some first.") 