# Generated by Django 5.1.4 on 2025-02-09 12:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu_resources', '0007_remove_lessonfromhand_group_lessonfromhand_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonfromhand',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='edu_resources.room'),
        ),
    ]
