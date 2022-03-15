from __future__ import print_function

import datetime, os
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
    else:
        return None

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_FILE = BASE_DIR / 'service/service.json'
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
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

def is_between(now, start, end):
    return start <= now <= end

def get_current_block():
    # now = datetime.datetime.now().time()
    now = datetime.time(12, 54)
    date = timezone.now().strftime("%Y-%m-%d")

    try:
        todays_type = get_calendar_events(Calendar_Type.SpecialEvents)[date][0]
    except KeyError:
        # print("Failed to get today's type!")
        # print(get_calendar_events(Calendar_Type.SpecialEvents))
        todays_type = Day_Type.Normal 

    try:
        todays_block = get_calendar_events(Calendar_Type.ABSchedule)[date]
    except KeyError:
        # print("Failed to figure out if today is an A day or B day!")
        return [Block.Outside_Hours]

    early_release_blocks = [
        (datetime.time(7, 35), datetime.time(8, 24), (Block.First, Block.Fifth)),
        (datetime.time(8, 25), datetime.time(8, 29), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(8, 30), datetime.time(9, 19), (Block.Second, Block.Sixth)),
        (datetime.time(9, 20), datetime.time(9, 24), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(9, 25), datetime.time(10, 14), (Block.Third, Block.Seventh)),
        (datetime.time(10, 15), datetime.time(10, 19), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(10, 20), datetime.time(11, 15), (Block.Fourth, Block.Eighth)),
    ]

    late_arrival_blocks = [
        (datetime.time(9, 35), datetime.time(10, 34), (Block.First, Block.Fifth)),
        (datetime.time(10, 35), datetime.time(10, 39), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(10, 40), datetime.time(11, 39), (Block.Second, Block.Sixth)),
        (datetime.time(11, 40), datetime.time(11, 44), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(11, 45), datetime.time(13, 14), (Block.Third, Block.Seventh)),
        (datetime.time(13, 15), datetime.time(13, 19), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(13, 20), datetime.time(14, 20), (Block.Fourth, Block.Eighth)),
    ]
    late_arrival_lunches = [
        (datetime.time(11, 45), datetime.time(12, 10), Block.First_Lunch),
        (datetime.time(12, 15), datetime.time(12, 40), Block.Second_Lunch),
        (datetime.time(12, 50), datetime.time(13, 15), Block.Third_Lunch),
    ]

    normal_blocks = [
        (datetime.time(7, 35), datetime.time(8, 54), (Block.First, Block.Fifth)),
        (datetime.time(8, 55), datetime.time(8, 59), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(9, 0), datetime.time(10, 19), (Block.Second, Block.Sixth)),
        (datetime.time(10, 20), datetime.time(10, 24), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(10, 25), datetime.time(10, 59), (Block.Bear_Block, Block.Bear_Block)),
        (datetime.time(11, 0), datetime.time(11, 4), (Block.Between_Classes, Block.Between_Classes)),\
        (datetime.time(11, 5), datetime.time(12, 54), (Block.Third, Block.Seventh)),
        (datetime.time(12, 55), datetime.time(12, 59), (Block.Between_Classes, Block.Between_Classes)),
        (datetime.time(13, 0), datetime.time(14, 20), (Block.Fourth, Block.Eighth)),
    ]
    normal_lunches = [
        (datetime.time(11, 5), datetime.time(11, 30), Block.First_Lunch),
        (datetime.time(11, 45), datetime.time(12, 10), Block.Second_Lunch),
        (datetime.time(12, 30), datetime.time(12, 55), Block.Third_Lunch),
    ]

    if todays_type in [Day_Type.Student_Holiday, Day_Type.Student_Teacher_Holiday]:
        return [Block.Outside_Hours]
    elif todays_type == Day_Type.Early_Release:
        for start, end, (a_day, b_day) in early_release_blocks:
            if start <= now <= end:
                return [a_day if todays_block == "A" else b_day]
        return [Block.Outside_Hours]
    else:
        blocks, lunches = (late_arrival_blocks, late_arrival_lunches) if todays_type == Day_Type.Late_Arrival else (normal_blocks, normal_lunches)
        for start, end, (a_day, b_day) in blocks:
            if start <= now <= end:
                returnable = [a_day if todays_block == "A" else b_day]
                if a_day == Block.Third:
                    for lunch_start, lunch_end, lunch in lunches:
                        if lunch_start <= now <= lunch_end:
                            returnable.append(lunch)
                            break
                return returnable
        return [Block.Outside_Hours]