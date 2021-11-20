from django.urls import path

from . import views

urlpatterns = [
    path('', views.ScheduleView.as_view()),

    path('calendars/', views.ScheduleCalendarListView.as_view()),
    path('calendars/<int:calendar_id>/', views.ScheduleCalendarInstanceView.as_view()),

    path('updateservice/', views.ServiceUpdateView.as_view()),

]