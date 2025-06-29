# Generated manually to fix NULL total_days in Leave model

from django.db import migrations

def fix_total_days(apps, schema_editor):
    Leave = apps.get_model('department', 'Leave')
    for leave in Leave.objects.all():
        if leave.total_days is None:
            delta = leave.end_date - leave.start_date
            leave.total_days = delta.days + 1
            leave.save()

class Migration(migrations.Migration):

    dependencies = [
        ('department', '0004_leave_leavequota'),
    ]

    operations = [
        migrations.RunPython(fix_total_days, reverse_code=migrations.RunPython.noop),
    ] 