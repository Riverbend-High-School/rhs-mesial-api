from django.urls import path

from . import views

urlpatterns = [
    path('msgnotice/', views.MessageNoticeView.as_view()),
    path('activeslides/', views.ActiveSlideView.as_view()),
]