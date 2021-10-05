# Generated by Django 3.2.4 on 2021-10-05 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20210923_2200'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendar_id', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=50)),
                ('enabled', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Events Calendar',
            },
        ),
        migrations.AlterModelOptions(
            name='lightnotice',
            options={'verbose_name': 'Light Notice'},
        ),
        migrations.AlterModelOptions(
            name='messagenotice',
            options={'verbose_name': 'Message Notice'},
        ),
        migrations.AlterModelOptions(
            name='slide',
            options={'verbose_name': 'Slide'},
        ),
    ]