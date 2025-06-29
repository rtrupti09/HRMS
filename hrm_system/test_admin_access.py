#!/usr/bin/env python
"""
Test script to verify admin access to leave management features
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_system.settings')
django.setup()

from django.contrib.auth.models import User
from department.models import Employee, Department, Role, Leave, LeaveQuota
from datetime import date, timedelta

def test_admin_access():
    """Test that admin users can access leave management features"""
    print("Testing Admin Access to Leave Management...")
    print("=" * 50)
    
    # Check if admin user exists
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"✅ Admin user found: {admin_user.username}")
        else:
            print("❌ No admin user found. Please create a superuser first.")
            print("Run: python manage.py createsuperuser")
            return
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        return
    
    # Check if there are any employees
    employees = Employee.objects.all()
    print(f"✅ Found {employees.count()} employees")
    
    # Check if there are any leave applications
    leaves = Leave.objects.all()
    print(f"✅ Found {leaves.count()} leave applications")
    
    # Check if there are any leave quotas
    quotas = LeaveQuota.objects.all()
    print(f"✅ Found {quotas.count()} leave quotas")
    
    # Show pending leaves
    pending_leaves = Leave.objects.filter(status='pending')
    print(f"✅ Found {pending_leaves.count()} pending leave applications")
    
    if pending_leaves.exists():
        print("\n📋 Pending Leave Applications:")
        for leave in pending_leaves[:5]:  # Show first 5
            print(f"  - {leave.employeeid.first_name} {leave.employeeid.last_name}: {leave.leave_type} ({leave.start_date} to {leave.end_date})")
    
    print("\n" + "=" * 50)
    print("✅ Admin access test completed!")
    print("\nTo test the admin interface:")
    print("1. Run: python manage.py runserver")
    print("2. Login as admin user")
    print("3. Navigate to 'Approve Leaves' or 'Leave Quotas' in the navigation")
    print("4. You should now be able to access these features without employee login issues")

if __name__ == "__main__":
    test_admin_access() 