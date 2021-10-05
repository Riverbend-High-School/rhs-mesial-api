from django.urls import path

from . import views

urlpatterns = [
    path('msgnotice/', views.MessageNoticeListView.as_view()),
    path('activeslides/', views.ActiveSlideListView.as_view()),
    path('events/', views.UpcomingEventsListView.as_view()),
]