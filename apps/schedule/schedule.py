from __future__ import print_function

import datetime, os, json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.utils import timezone
from enum import Enum

from rhs_mesial_api.settings import BASE_DIR

from .models import ScheduleCalendar


global_events = []

class Calendar_Type(str, Enum):
    ABSchedule = "ABSchedule"
    SpecialEvents = "SpecialEvents"

class Day_Type(str, Enum):
    Early_Release = "Early Release"
    Late_Arrival = "Late Arrival"
    Student_Teacher_Holiday = "Student/Teacher Holiday"
    Student_Holiday = "Student Holiday"
    Other = "Other"
    Normal = "Normal"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

class Block(Enum):
    First = "A1"
    Second = "A2"
    Third = "A3"
    Fourth = "A4"
    Fifth = "B5"
    Sixth = "B6"
    Seventh = "B7"
    Eighth = "B8"
    First_Lunch = "First Lunch"
    Second_Lunch = "Second Lunch"
    Third_Lunch = "Third Lunch"
    Bear_Block = "Bear Block"
    Outside_Hours = "Outside Hours"
    Between_Classes = "Between Classes"

    def __str__(self):
        return self.value

def sort_special_events(event):
    date = event['start'].get('dateTime', event['start'].get('date'))
    summary = event['summary'].strip()
    out = Day_Type.Other
    if "Early Release" in summary:
        out = Day_Type.Early_Release
    elif "Student/Teacher Holiday" in summary:
        out = Day_Type.Student_Teacher_Holiday
    elif "Student Holiday" in summary:
        out = Day_Type.Student_Holiday
    return (date, (out, summary))

def get_calendar_events(calendar_type):
    """
        calendar_type (Calendar_Type) : Enum specificying the calendar you wish to access
    """

    if calendar_type == Calendar_Type.ABSchedule:
        map_func = lambda event: (event['start'].get('dateTime', event['start'].get('date')), event['summary'].strip()[:1])
        calendar_id = ScheduleCalendar.objects.filter(calendar_type=1).first().calendar_id
    elif calendar_type == Calendar_Type.SpecialEvents:
        map_func = sort_special_events
        calendar_id = ScheduleCalendar.objects.filter(calendar_type=2).first().calendar_id

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = service_account.Credentials.from_service_account_info(json.loads(os.getenv('SERVICE_JSON')), scopes=SCOPES)
    
    map_func = None
    calendar_id = ""

    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendar_id, timeMin=now, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return dict(map(map_func, events))

def get_current_day_type():
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    try:
        todays_type = get_calendar_events(Calendar_Type.SpecialEvents)[date][0]
    except KeyError:
        todays_type = Day_Type.Normal 
    
    return [todays_type]

def get_current_block():
    # I hate this :)
    now = timezone.now()
    date = now.strftime("%Y-%m-%d")
    hours = now.hour
    minutes = now.minute
    try:
        todays_type = get_calendar_events(Calendar_Type.SpecialEvents)[date][0]
    except KeyError:
        todays_type = Day_Type.Normal 

    try:
        todays_block = get_calendar_events(Calendar_Type.ABSchedule)[date]
    except KeyError:
        return [Block.Outside_Hours]

    if todays_type in [Day_Type.Student_Holiday, Day_Type.Student_Teacher_Holiday]:
        return [Block.Outside_Hours]
    elif todays_type == Day_Type.Early_Release:
        if (hours == 7 and minutes >= 35) or (hours == 8 and minutes <= 25):
            return [Block.First if todays_block == "A" else Block.Fifth]
        elif (hours == 8 and 25 < minutes < 30):
            return [Block.Between_Classes]
        elif (hours == 8 and minutes >= 30) or (hours == 9 and minutes <= 20):
            return [Block.Second if todays_block == "A" else Block.Sixth]
        elif hours == 9 and 20 < minutes < 25:
            return [Block.Between_Classes]
        elif (hours == 9 and minutes >= 25) or (hours == 10 and minutes <= 15):
            return [Block.Third if todays_block == "A" else Block.Seventh]
        elif hours == 10 and 15 < minutes < 20:
            return [Block.Between_Classes]
        elif hours == 10 or (hours == 11 and minutes <= 15):
            return [Block.Fourth if todays_block == "A" else Block.Eighth]
        else:
            return [Block.Outside_Hours]
    elif todays_type == Day_Type.Late_Arrival:
        if (hours == 9 and minutes >= 35) or (hours == 10 and minutes <= 35):
            return [Block.First if todays_block == "A" else Block.Fifth]
        elif (hours == 10 and 35 < minutes < 40):
            return [Block.Between_Classes]
        elif (hours == 10 and minutes >= 40) or (hours == 11 and minutes <= 40):
            return [Block.Second if todays_block == "A" else Block.Sixth]
        elif hours == 11 and 40 < minutes < 45:
            return [Block.Between_Classes]
        elif (hours == 11 and minutes >= 45) or (hours == 1 and minutes <= 15):
            day_block = Block.Third if todays_block == "A" else Block.Seventh
            if (hours == 11 and minutes >= 45) or (hours == 12 and minutes <= 10):
                return [day_block, Block.First_Lunch]
            elif hours == 12 and 15 <= minutes <= 40:
                return [day_block, Block.Second_Lunch]
            elif (hours == 12 and minutes >= 50) or (hours == 1 and minutes <= 15):
                return [day_block, Block.Third_Lunch]
            else:
                return [day_block]
        elif hours == 13 and 15 < minutes < 20:
            return [Block.Between_Classes]
        elif (hours == 13 and minutes >= 20) or (hours == 14 and minutes <= 20):
            return [Block.Fourth if todays_block == "A" else Block.Eighth]
        else:
            return [Block.Outside_Hours]
    else:
        if (hours == 7 and minutes >= 35) or (hours == 8 and minutes <= 55):
            return [Block.First if todays_block == "A" else Block.Fifth]
        elif (hours == 8 and minutes > 55):
            return [Block.Between_Classes]
        elif hours == 9 or (hours == 10 and minutes <= 20):
            return [Block.Second if todays_block == "A" else Block.Sixth]
        elif hours == 10 and 20 < minutes < 25:
            return [Block.Between_Classes]
        elif (hours == 10 and minutes >= 25) or (hours == 11 and minutes == 0):
            return [Block.Bear_Block]
        elif hours == 11 and 0 < minutes < 5:
            return [Block.Between_Classes]
        elif (hours == 11 and minutes >= 5) or (hours == 12 and minutes <= 55):
            day_block = Block.Third if todays_block == "A" else Block.Seventh
            if hours == 11 and 5 <= minutes <= 30:
                return [day_block, Block.First_Lunch]
            elif (hours == 11 and minutes >= 45) or (hours == 12 and minutes <= 10):
                return [day_block, Block.Second_Lunch]
            elif hours == 12 and 30 <= minutes <= 55:
                return [day_block, Block.Third_Lunch]
            else:
                return [day_block]
        elif hours == 12 and minutes > 55:
            return [Block.Between_Classes]
        elif hours == 13 or (hours == 14 and minutes <= 20):
            return [Block.Fourth if todays_block == "A" else Block.Eighth]
        else:
            return [Block.Outside_Hours]