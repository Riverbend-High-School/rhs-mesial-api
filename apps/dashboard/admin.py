from django.contrib import admin

from .models import *

@admin.register(MessageNotice)
class MessageNoticeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MessageNotice._meta.get_fields()]

@admin.register(LightNotice)
class LightNoticeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LightNotice._meta.get_fields()]

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('message', 'type', 'author', 'path')

@admin.register(EventCalendar)
class EventCalendarAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EventCalendar._meta.get_fields()]