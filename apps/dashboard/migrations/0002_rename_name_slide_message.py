# Generated by Django 3.2.4 on 2021-09-24 01:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='slide',
            old_name='name',
            new_name='message',
        ),
    ]
