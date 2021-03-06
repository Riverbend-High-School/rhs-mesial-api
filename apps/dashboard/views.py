import os
import re
from datetime import date, datetime as dt
from datetime import timedelta as td
from django.utils import timezone
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
                if len(events[key]) > 0:
                    events[key] = sorted(events[key], key=lambda x: x['start'])
                if len(events[key]) > 5:
                    events[key] = events[key][:5]

        return Response(events, status=status.HTTP_200_OK)

def map_events(event_tuple):
    event, time_period = event_tuple
    out = {
        "start": event['start'].get('dateTime', event['start'].get('date')), 
        "end": event['end'].get('dateTime', event['end'].get('date')),
        "all_day": 'date' in event['start'],
        "summary": event['summary'].strip(),
        "location": event['location'] if 'location' in event else None
    }

    if out["all_day"]:
        working_day = ""
        if time_period == "today":
            working_day = dt.now().strftime('%Y-%m-%d')
        elif time_period == "tomorrow":
            working_day = (dt.now() + td(days=1)).strftime('%Y-%m-%d')
        else:
            return out

        start = dt.strptime(out["start"], '%Y-%m-%d')
        end = dt.strptime(out["end"], '%Y-%m-%d')

        if start + td(days=1) == end and working_day == out["end"]:
            return None
    return out

def get_calendar_events(calendar_id):
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = service_account.Credentials.from_service_account_file(BASE_DIR / 'service/service.json', scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    eod_td = td(hours=23, minutes=59)
    timezone_str = '-04:00'
    
    now_raw = timezone.now()
    now = datetime(now_raw.year, now_raw.month, now_raw.day)
    eod = now + eod_td
    now_str = now.isoformat() + timezone_str # 'Z' indicates UTC time
    eod_str = eod.isoformat() + timezone_str
    tomorrow = now + td(days=1)
    tomorrow_eod = tomorrow + eod_td
    tomorrow_str = tomorrow.isoformat() + timezone_str
    tomorrow_eod_str = tomorrow_eod.isoformat() + timezone_str
    two_days = tomorrow + td(days=1)
    two_days_eod = tomorrow + td(days=5) + eod_td
    two_str = two_days.isoformat() + timezone_str
    two_days_eod_str = two_days_eod.isoformat() + timezone_str
    later = tomorrow + td(days=6)
    later_str = later.isoformat() + timezone_str

    now_events_result = service.events().list(calendarId=calendar_id, timeMin=now_str, timeMax=eod_str, singleEvents=True, orderBy='startTime', maxResults=5).execute()
    tomorrow_events_result = service.events().list(calendarId=calendar_id, timeMin=tomorrow_str, timeMax=tomorrow_eod_str, singleEvents=True, orderBy='startTime', maxResults=5).execute()
    week_events_result = service.events().list(calendarId=calendar_id, timeMin=two_str, timeMax=two_days_eod_str, singleEvents=True, orderBy='startTime', maxResults=5).execute()
    later_events_result = service.events().list(calendarId=calendar_id, timeMin=later_str, singleEvents=True, orderBy='startTime', maxResults=5).execute()

    #{start, end, summary, location}
    filter_none = lambda x: x != None

    today_raw = now_events_result.get('items', [])
    today = list(filter(filter_none, map(map_events, zip(today_raw, ['today'] * len(today_raw)))))

    tomorrow_raw = tomorrow_events_result.get('items', [])
    tomorrow = list(filter(filter_none, map(map_events, zip(tomorrow_raw, ['tomorrow'] * len(tomorrow_raw)))))

    week_raw = week_events_result.get('items', [])
    week = list(map(map_events, zip(week_raw, [0] * len(week_raw))))

    later_raw = later_events_result.get('items', [])
    later = list(map(map_events, zip(later_raw, [0] * len(later_raw))))

    #print(events)

    out = {"today": today, "tomorrow": tomorrow, "week": week, "later": later}
    #print(out)
    return out
