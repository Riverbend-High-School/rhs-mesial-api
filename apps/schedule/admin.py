from django.contrib import admin

from .models import *

@admin.register(ScheduleCalendar)
class ScheduleCalendarAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ScheduleCalendar._meta.get_fields()]

@admin.register(GoogleAPIServiceJSON)
class GoogleAPIServiceJSON(admin.ModelAdmin):
    list_display = [field.name for field in GoogleAPIServiceJSON._meta.get_fields()]