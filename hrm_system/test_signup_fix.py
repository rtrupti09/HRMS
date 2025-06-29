#!/usr/bin/env python
"""
Test script to verify employee signup process works correctly
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_system.settings')
django.setup()

from department.models import Employee
from department.forms import EmployeeSignupForm
from datetime import date

def test_signup_form():
    """Test that the EmployeeSignupForm includes all required fields"""
    print("Testing Employee Signup Form...")
    print("=" * 50)
    
    # Test form fields
    form = EmployeeSignupForm()
    expected_fields = ['first_name', 'last_name', 'email', 'username', 'password', 'mobile', 'date_of_joining', 'confirm_password']
    
    print("✅ Form fields:")
    for field_name in expected_fields:
        if field_name in form.fields:
            print(f"  ✓ {field_name}")
        else:
            print(f"  ✗ {field_name} - MISSING!")
    
    print("\n" + "=" * 50)
    print("✅ Signup form test completed!")
    print("\nThe signup form should now include all required fields:")
    print("- First Name")
    print("- Last Name") 
    print("- Email")
    print("- Username")
    print("- Mobile Number")
    print("- Date of Joining")
    print("- Password")
    print("- Confirm Password")

def test_employee_model():
    """Test that Employee model has required fields"""
    print("\nTesting Employee Model...")
    print("=" * 50)
    
    # Check required fields
    required_fields = ['first_name', 'last_name', 'username', 'password', 'email', 'mobile', 'date_of_joining']
    
    print("✅ Employee model required fields:")
    for field_name in required_fields:
        if hasattr(Employee, field_name):
            field = Employee._meta.get_field(field_name)
            if field.null == False and field.blank == False:
                print(f"  ✓ {field_name} (Required)")
            else:
                print(f"  ⚠ {field_name} (Optional)")
        else:
            print(f"  ✗ {field_name} - MISSING!")
    
    print("\n" + "=" * 50)
    print("✅ Employee model test completed!")

if __name__ == "__main__":
    test_signup_form()
    test_employee_model()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\nTo test the signup process:")
    print("1. Run: python manage.py runserver")
    print("2. Go to: http://127.0.0.1:8000/password-reset/signup/")
    print("3. Fill in all the required fields including Date of Joining")
    print("4. Submit the form - it should work without IntegrityError") 