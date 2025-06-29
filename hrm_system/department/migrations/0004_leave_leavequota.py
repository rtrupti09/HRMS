# Generated manually for Leave Management System

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0003_performancereview'),
    ]

    operations = [
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('leaveid', models.AutoField(primary_key=True, serialize=False)),
                ('leave_type', models.CharField(choices=[('SL', 'Sick Leave'), ('CL', 'Casual Leave'), ('PL', 'Privilege Leave'), ('LWP', 'Leave Without Pay')], max_length=3)),
                ('reason', models.CharField(max_length=200)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_days', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to='department.employee')),
                ('employeeid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='department.employee')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveQuota',
            fields=[
                ('quotaid', models.AutoField(primary_key=True, serialize=False)),
                ('leave_type', models.CharField(choices=[('SL', 'Sick Leave'), ('CL', 'Casual Leave'), ('PL', 'Privilege Leave'), ('LWP', 'Leave Without Pay')], max_length=3)),
                ('total_quota', models.IntegerField()),
                ('used_quota', models.IntegerField(default=0)),
                ('remain_quota', models.IntegerField()),
                ('year', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employeeid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_quotas', to='department.employee')),
            ],
            options={
                'unique_together': {('employeeid', 'leave_type', 'year')},
            },
        ),
    ] 