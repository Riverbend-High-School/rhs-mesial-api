from django.db import models
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.utils.dateformat import format

class ScheduleCalendar(models.Model):
    TYPES = (
        (0, 'Other'),
        (1, 'SCPS A/B Day Calendar'),
        (2, 'SCPS Instructional Calendar'),
    )

    calendar_type = models.IntegerField(default=0, choices=TYPES)
    calendar_id = models.CharField(max_length=255)