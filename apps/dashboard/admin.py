from django.contrib import admin

from .models import *

@admin.register(MessageNotice)
class ScheduleCalendarAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MessageNotice._meta.get_fields()]

@admin.register(LightNotice)
class ScheduleCalendarAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LightNotice._meta.get_fields()]

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('message', 'type', 'author', 'path')