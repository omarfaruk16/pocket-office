# Generated by Django 5.2.1 on 2025-06-01 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0003_todo_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='todo',
            old_name='teacher',
            new_name='user',
        ),
    ]
