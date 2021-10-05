import os
import re
from datetime import date, datetime as dt
from datetime import timedelta as td
from urllib.parse import scheme_chars
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from googleapiclient.discovery import build
from google.oauth2 import service_account

from rhs_mesial_api.settings import BASE_DIR

from .serializers import *
from .models import *

class MessageNoticeListView(APIView):
    def get (self, request):
        """
        Get the message notice.
        """
        notice = MessageNotice.objects.all().first()
        serializer = MessageNoticeSerializer(notice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post (self, request):
        """
        Posting a new message notice will delete all prior message notices
        """
        old_notices = MessageNotice.objects.all()
        old_notices.delete()

        serializer = MessageNoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActiveSlideListView(APIView):
    def get (self, request):
        """
        Get the message notice.
        """
        notice = Slide.objects.all().filter(approved=True, type=1, start__lte=datetime.now(), end__gte=datetime.now())
        serializer = ActiveSlideSerializer(notice, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpcomingEventsListView(APIView):
    def get (self, request):
        """
        Get the message notice.
        """
        calendars = EventCalendar.objects.all().filter(enabled=True)

        events = {'today': [], 'tomorrow': [], 'week': [], 'later': []}

        for cal in calendars:
            this_events = get_calendar_events(cal.calendar_id)
            #print(this_events)
            for (key, event_list) in this_events.items():
                for event in event_list:
                    events[key].append(event)

        if len(events['today']) > 0:
            # print(events)
            events['today'].sort(key=lambda event: event['start'])
        if len(events['tomorrow']) > 0:
            events['tomorrow'].sort(key=lambda event: event['start'])
        if len(events['later']) > 0:
            events['later'].sort(key=lambda event: event['start'])

        return Response(events, status=status.HTTP_200_OK)
    
def get_calendar_events(calendar_id):

    creds = None
    SERVICE_ACCOUNT_FILE = BASE_DIR / 'service.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendar_id, timeMin=now, singleEvents=True, orderBy='startTime', maxResults=5).execute()
    events = events_result.get('items', [])
    
    #{start, end, summary, location}
    today = []
    tomorrow = []
    week = []
    later = []

    now = dt.now()

    for event in events:
        all_day = 'date' in event['start']
        obj = {
                "start": event['start'].get('dateTime', event['start'].get('date')), 
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "all_day": all_day,
                "summary": event['summary'].strip(),
                "location": event['location'] if 'location' in event else None
        }
        if all_day:
            time = date.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            time = datetime(time.year, time.month, time.day)
        else:
            time = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        #print(time.strftime('%Y-%m-%d'))
        if time.strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):
            today.append(obj)
        elif time.strftime('%Y-%m-%d') == (now + td(days=1)).strftime('%Y-%m-%d'):
            tomorrow.append(obj)
        elif (now + td(days=2)) < time < (now + td(days=7)):
            week.append(obj)
        else:
            later.append(obj)

    #print(events)

    out = {"today": today, "tomorrow": tomorrow, "week": week, "later": later}
    #print(out)
    return out
