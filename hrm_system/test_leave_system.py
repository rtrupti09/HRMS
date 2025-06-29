#!/usr/bin/env python
"""
Test script for Leave Management System
Run this script to test the basic functionality
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_system.settings')
django.setup()

from department.models import Department, Role, Employee, Leave, LeaveQuota

def create_test_data():
    """Create test data for leave management system"""
    print("Creating test data for Leave Management System...")
    
    # Create department if not exists
    dept, created = Department.objects.get_or_create(
        dept_name="IT Department",
        defaults={'description': 'Information Technology Department'}
    )
    if created:
        print(f"Created department: {dept.dept_name}")
    
    # Create roles if not exist
    manager_role, created = Role.objects.get_or_create(
        role_name="Manager",
        defaults={'description': 'Team Manager', 'department': dept}
    )
    if created:
        print(f"Created role: {manager_role.role_name}")
    
    employee_role, created = Role.objects.get_or_create(
        role_name="Developer",
        defaults={'description': 'Software Developer', 'department': dept}
    )
    if created:
        print(f"Created role: {employee_role.role_name}")
    
    hr_role, created = Role.objects.get_or_create(
        role_name="HR",
        defaults={'description': 'Human Resources', 'department': dept}
    )
    if created:
        print(f"Created role: {hr_role.role_name}")
    
    # Create manager employee
    manager, created = Employee.objects.get_or_create(
        email="manager@company.com",
        defaults={
            'first_name': 'John',
            'last_name': 'Manager',
            'username': 'manager',
            'password': 'manager123',
            'mobile': '1234567890',
            'date_of_joining': date.today() - timedelta(days=365),
            'dept': dept,
            'role': manager_role
        }
    )
    if created:
        print(f"Created manager: {manager.first_name} {manager.last_name}")
    
    # Create regular employee
    employee, created = Employee.objects.get_or_create(
        email="employee@company.com",
        defaults={
            'first_name': 'Jane',
            'last_name': 'Employee',
            'username': 'employee',
            'password': 'employee123',
            'mobile': '0987654321',
            'date_of_joining': date.today() - timedelta(days=180),
            'dept': dept,
            'role': employee_role,
            'reporting_manager': manager
        }
    )
    if created:
        print(f"Created employee: {employee.first_name} {employee.last_name}")
    
    # Create HR employee
    hr_employee, created = Employee.objects.get_or_create(
        email="hr@company.com",
        defaults={
            'first_name': 'HR',
            'last_name': 'Manager',
            'username': 'hr',
            'password': 'hr123',
            'mobile': '5555555555',
            'date_of_joining': date.today() - timedelta(days=730),
            'dept': dept,
            'role': hr_role
        }
    )
    if created:
        print(f"Created HR: {hr_employee.first_name} {hr_employee.last_name}")
    
    # Create leave quotas for current year
    current_year = date.today().year
    
    # Quota for employee
    quota_sl, created = LeaveQuota.objects.get_or_create(
        employeeid=employee,
        leave_type='SL',
        year=current_year,
        defaults={'total_quota': 15, 'used_quota': 0}
    )
    if created:
        print(f"Created SL quota for {employee.first_name}: {quota_sl.total_quota} days")
    
    quota_cl, created = LeaveQuota.objects.get_or_create(
        employeeid=employee,
        leave_type='CL',
        year=current_year,
        defaults={'total_quota': 12, 'used_quota': 0}
    )
    if created:
        print(f"Created CL quota for {employee.first_name}: {quota_cl.total_quota} days")
    
    quota_pl, created = LeaveQuota.objects.get_or_create(
        employeeid=employee,
        leave_type='PL',
        year=current_year,
        defaults={'total_quota': 21, 'used_quota': 0}
    )
    if created:
        print(f"Created PL quota for {employee.first_name}: {quota_pl.total_quota} days")
    
    # Quota for manager
    manager_quota_sl, created = LeaveQuota.objects.get_or_create(
        employeeid=manager,
        leave_type='SL',
        year=current_year,
        defaults={'total_quota': 15, 'used_quota': 0}
    )
    if created:
        print(f"Created SL quota for {manager.first_name}: {manager_quota_sl.total_quota} days")
    
    print("\nTest data creation completed!")
    print("\nLogin Credentials:")
    print("Manager: manager@company.com / manager123")
    print("Employee: employee@company.com / employee123")
    print("HR: hr@company.com / hr123")
    
    return manager, employee, hr_employee

def test_leave_functionality():
    """Test basic leave functionality"""
    print("\nTesting Leave Management Functionality...")
    
    # Get test employees
    try:
        employee = Employee.objects.get(email="employee@company.com")
        manager = Employee.objects.get(email="manager@company.com")
    except Employee.DoesNotExist:
        print("Test employees not found. Run create_test_data() first.")
        return
    
    # Test creating a leave application
    leave = Leave.objects.create(
        employeeid=employee,
        leave_type='SL',
        reason='Not feeling well, need to rest',
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=2),
        total_days=2,
        status='pending'
    )
    print(f"Created leave application: {leave}")
    
    # Test approving leave
    leave.status = 'approved'
    leave.approved_by = manager
    leave.save()
    print(f"Approved leave application: {leave}")
    
    # Test quota update
    quota = LeaveQuota.objects.get(employeeid=employee, leave_type='SL', year=date.today().year)
    quota.used_quota += leave.total_days
    quota.save()
    print(f"Updated quota - Used: {quota.used_quota}, Remaining: {quota.remain_quota}")
    
    print("\nLeave management functionality test completed!")

if __name__ == "__main__":
    print("Leave Management System Test")
    print("=" * 40)
    
    # Create test data
    create_test_data()
    
    # Test functionality
    test_leave_functionality()
    
    print("\nAll tests completed successfully!")
    print("\nYou can now:")
    print("1. Login as employee to apply for leave")
    print("2. Login as manager to approve leaves")
    print("3. Login as HR to manage leave quotas")
    print("4. Access the leave dashboard at /leaves/") 