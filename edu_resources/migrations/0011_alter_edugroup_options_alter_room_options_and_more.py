# Generated by Django 5.1.4 on 2025-02-09 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu_resources', '0010_alter_lessonfromhand_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='edugroup',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='teacherfromhand',
            options={'ordering': ['name']},
        ),
    ]
