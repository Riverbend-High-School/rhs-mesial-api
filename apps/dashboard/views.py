import os, datetime
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

        events = []

        for cal in calendars:
            for event in get_calendar_events(cal.calendar_id):
                events.append(event)

        events.sort(key=lambda event: event['start'])

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

    return map(lambda event:    {
                                    "start": event['start'].get('dateTime', event['start'].get('date')), 
                                    "end": event['end'].get('dateTime', event['end'].get('date')), 
                                    "summary": event['summary'].strip(),
                                    "location": event['location'] if 'location' in event else None
                                }, events)
