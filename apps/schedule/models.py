from django.db import models
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.utils.dateformat import format

class ScheduleCalendar(models.Model):
    class Meta:
        verbose_name = 'Schedule Calendar'

    TYPES = (
        (0, 'Other'),
        (1, 'SCPS A/B Day Calendar'),
        (2, 'SCPS Instructional Calendar'),
    )

    calendar_type = models.IntegerField(default=0, choices=TYPES)
    calendar_id = models.CharField(max_length=255)

class GoogleAPIServiceJSON(models.Model):
    class Meta:
        verbose_name = 'Google API Service JSON'
    
    file = models.FileField(upload_to='service/')