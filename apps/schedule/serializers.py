from rest_framework import serializers

from .models import *

class ScheduleCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleCalendar
        fields = '__all__'
