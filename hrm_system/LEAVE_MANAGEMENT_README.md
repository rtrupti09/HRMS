# Leave Management System

A comprehensive leave management system integrated into the existing HRMS, allowing employees to apply for leave, managers to approve/reject applications, and HR to manage leave quotas.

## Features

### Employee Features
- **Leave Dashboard**: View leave balance and leave history
- **Apply Leave**: Submit leave applications with different types (SL, CL, PL, LWP)
- **Edit Leave**: Modify pending leave applications before approval
- **Leave Balance**: Real-time view of remaining leave quota

### Manager/Admin Features
- **Leave Approval Dashboard**: Review and approve/reject leave applications
- **Team Management**: Manage leaves for team members
- **Leave History**: View all leave applications

### HR Features
- **Leave Quota Management**: Set and manage leave quotas for employees
- **Quota Dashboard**: View all employee leave quotas with pagination
- **Year-wise Quotas**: Manage quotas for different years

## Database Design

### Leave Table
- `leaveid` (Primary Key): Unique identifier for leave request
- `employeeid` (Foreign Key): Link to employee table
- `leave_type` (Enum): SL, CL, PL, LWP
- `reason` (Varchar): Leave reason
- `start_date` (Date): Start date of leave
- `end_date` (Date): End date of leave
- `total_days` (Integer): Total number of leave days
- `status` (Enum): approved, rejected, pending
- `approved_by` (Foreign Key): Link to manager or HR in employee table

### Leave Quota Table
- `quotaid` (Primary Key): Unique identifier for leave quota
- `employeeid` (Foreign Key): Link to Employee Table
- `leave_type` (Enum): Type of Leave (SL, CL, PL, LWP)
- `total_quota` (Integer): Total leaves allowed per year
- `used_quota` (Integer): Used Leave quota
- `remain_quota` (Integer): Remaining Leave quota
- `year` (Integer): Year for the quota

## Installation & Setup

1. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Create Test Data** (Optional):
   ```bash
   python test_leave_system.py
   ```

3. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

## Usage

### For Employees
1. Login with employee credentials
2. Navigate to "Leaves" in the navigation menu
3. View your leave balance and history
4. Click "Apply Leave" to submit a new application
5. Edit pending applications if needed

### For Managers
1. Login with manager credentials
2. Navigate to "Approve Leaves" in the navigation menu
3. Review pending leave applications
4. Click "Review" to approve or reject applications

### For HR
1. Login with HR credentials
2. Navigate to "Leave Quotas" in the navigation menu
3. Add or edit leave quotas for employees
4. Manage quotas for different years

## URL Structure

- `/leaves/` - Employee leave dashboard
- `/leaves/apply/` - Apply for leave
- `/leaves/edit/<id>/` - Edit leave application
- `/leaves/admin/` - Manager leave approval dashboard
- `/leaves/approve/<id>/` - Approve/reject specific leave
- `/leaves/quota/` - HR leave quota management
- `/leaves/quota/add/` - Add new leave quota
- `/leaves/quota/edit/<id>/` - Edit leave quota

## Test Credentials

After running the test script, you can use these credentials:

- **Manager**: manager@company.com / manager123
- **Employee**: employee@company.com / employee123
- **HR**: hr@company.com / hr123

## Business Rules

1. **Leave Application**:
   - Employees can only apply for future dates
   - Leave quota is checked before allowing application
   - Total days are automatically calculated

2. **Leave Approval**:
   - Only managers can approve leaves for their team members
   - Once approved/rejected, leave cannot be edited
   - Approved leaves automatically update the quota

3. **Leave Quota**:
   - HR can set quotas for different leave types
   - Quotas are year-specific
   - Used quota cannot be manually modified
   - Remaining quota is automatically calculated

4. **Access Control**:
   - Employees can only see their own leaves
   - Managers can see leaves from their team members
   - HR can manage all leave quotas
   - Admins have full access

## UI Features

- **Responsive Design**: Works on desktop and mobile devices
- **Bootstrap 5**: Modern, clean interface
- **Bootstrap Icons**: Intuitive iconography
- **Pagination**: Efficient data display
- **Form Validation**: Client and server-side validation
- **Success/Error Messages**: Clear user feedback

## Technical Implementation

- **Django Models**: Well-structured database models
- **Django Forms**: Form handling with validation
- **Django Views**: Business logic implementation
- **Django Templates**: Reusable template components
- **Django Admin**: Built-in admin interface for data management

## Future Enhancements

1. **Email Notifications**: Send emails for leave applications and approvals
2. **Calendar Integration**: Sync with external calendars
3. **Leave Reports**: Generate leave reports and analytics
4. **Mobile App**: Native mobile application
5. **API Endpoints**: REST API for external integrations
6. **Leave Policies**: Configurable leave policies
7. **Holiday Calendar**: Integration with holiday calendar
8. **Leave Cancellation**: Allow employees to cancel approved leaves

## Support

For any issues or questions regarding the Leave Management System, please refer to the main HRMS documentation or contact the development team. 