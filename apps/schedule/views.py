import os
from urllib.parse import scheme_chars
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import *
from .schedule import *

class ScheduleCalendarListView(APIView):
    def get (self, request):
        """
        Get all schedule calendars.
        """
        calendars = ScheduleCalendar.objects.all()
        serializer = ScheduleCalendarSerializer(calendars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post (self, request):
        """
        Add a new schedule calendar.
        """
        serializer = ScheduleCalendarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScheduleCalendarInstanceView(APIView):
    def put(self, request, calendar_id):
        """
        Update a schedule calendar.
        """
        calendar = get_object_or_404(ScheduleCalendar, id=calendar_id)
        serializer = ScheduleCalendarSerializer(calendar, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ScheduleView(APIView):
    def get(self, request):
            
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        block_list = get_current_block()
        block = block_list[0]
        try:
            lunch = block_list[1]
        except:
            lunch = None


        'Simple_Block "A3" "N/A" '
        'Full_Block "A3 (First Lunch)" "Outside Hours"'
        """
            Response will be in JSON format:

            {
                "block" : {formatted block},
                "simple_block" : {simple formatted block},
            }
            
        """
        block_str = f"{block}{f' ({lunch})' if not lunch is None else ''}"
        simple_str = f"{block}"

        
        if block == Block.Bear_Block:
            simple_str = "BB"
        elif block == Block.Outside_Hours:
            simple_str = "N/A"

        schedule_list = get_current_day_type()
        print(schedule_list)
        schedule = schedule_list[0]


        json = {
            "schedule": schedule,
            "block": block_str,
            "simple_block": simple_str,
        }

        return Response(json, status=status.HTTP_200_OK)


