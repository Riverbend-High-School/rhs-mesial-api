import os
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.utils.dateformat import format

class MessageNotice(models.Model):
    class Meta:
        verbose_name = 'Message Notice'

    TYPES = (
        (0, 'Normal'),
        (1, 'Warning'),
        (2, 'Critical'),
    )

    type = models.IntegerField(default=0, choices=TYPES)
    message = models.CharField(max_length=50)
    author = models.CharField(max_length=50)


class LightNotice(models.Model):
    class Meta:
        verbose_name = 'Light Notice'

    TYPES = (
        (0, 'Other'),
        (1, 'Student Tech Team'),
        (3, '3D Printer Status'),
    )

    STATUS = (
        (0, 'Off'),
        (1, 'On'),
        (2, 'Flashing'),
    )

    type = models.IntegerField(default=0, choices=TYPES)
    status = models.IntegerField(default=0, choices=STATUS)
    author = models.CharField(max_length=50)
    

class Slide(models.Model):
    class Meta:
        verbose_name = 'Slide'

    TYPES = (
        (0, 'Other'),
        (1, 'Daily Slide'),
    )

    message = models.CharField(max_length=32)
    type = models.IntegerField(default=0, choices=TYPES)
    reason = models.TextField()
    author = models.CharField(max_length=50)
    path = models.FileField(upload_to='slides/')
    start = models.DateTimeField()
    end = models.DateTimeField()
    approved = models.BooleanField(default=False)

    @property
    def extension(self):
        message, extension = os.path.splitext(self.path.name)
        return extension

    @property
    def size(self):
        return os.path.getsize(self.path.path)

    def __str__(self):
        return self.message