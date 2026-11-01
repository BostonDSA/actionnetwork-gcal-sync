from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from test.data.solidarity_tech_events import (
    single_in_person_event,
    single_virtual_event,
    recurring_in_person_event,
    recurring_virtual_event,
    recurring_hybrid_event,
)
from event_connectors import SolidarityTech

def test_translate_single_in_person_event():
    """
    Event in ST has the event parent and then one in person session
    This should result in 1 calendar event 
    """
    parsed_events = SolidarityTech._translate_event(single_in_person_event)

    assert len(parsed_events) == 1

    event = parsed_events[0]
    assert event.primary_session_id == 133550
    assert event.parent_id == 44782
    assert event.title == "\"No On 5\" Canvass - Natick Centre"
    assert event.tags == [
        "New Member Friendly",
        "canvass",
        "Canvasses",
        "MetroWest",
        "Electoral Organizing Committee"
    ]
    assert event.location == "Newton Center, Centre St & Beacon St, Newton, MA 02459, USA"
    assert event.start == datetime(2026, 10, 23, hour=17, minute=0, second=0, tzinfo=ZoneInfo("America/New_York"))
    assert event.end == datetime(2026, 10, 23, hour=20, minute=0, second=0, tzinfo=ZoneInfo("America/New_York"))


def test_translate_single_virtual_event():
    """
    Event in ST has the event parent and then one virtual session
    This should result in 1 calendar event 
    """
    parsed_events = SolidarityTech._translate_event(single_virtual_event)

    assert len(parsed_events) == 1

    event = parsed_events[0]
    assert event.primary_session_id == 128291
    assert event.parent_id == 42645
    assert event.title == "Turnout Tuesday 10/13, Phonebank for Ballot Measure Campaign"
    assert event.location == "https://us02web.zoom.us/j/86460622382?pwd=UU4eaaUW88MzwOejaBDELujdb2sEII.1"
    assert event.event_page_url == "https://bostondsa.solidarity.tech/turnout-tuesday-10-10-phonebank-for-ballot-measure-campaign"
    assert event.start == datetime(2026, 10, 13, hour=17, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))
    assert event.end == datetime(2026, 10, 13, hour=19, minute=0, second=0, tzinfo=ZoneInfo("America/New_York"))


def test_translate_single_hybrid_event():
    pass


def test_translate_recurring_in_person_event():
    """
    Event in ST has the event parent and then two in person sessions
    This should result in 2 calendar event 
    """
    parsed_events = SolidarityTech._translate_event(recurring_in_person_event)

    assert len(parsed_events) == 2

    first_session = parsed_events[0]
    assert first_session.primary_session_id == 118929
    assert first_session.parent_id == 38385
    assert first_session.title == "Labor Circle"
    assert first_session.location == "Community Church of Boston, 565 Boylston St, Boston, MA 02116, USA"
    assert first_session.event_page_url == "https://bostondsa.solidarity.tech/labor-circle"
    assert first_session.start == datetime(2026, 11, 4, hour=18, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))
    assert first_session.end == datetime(2026, 11, 4, hour=20, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))

    second_session = parsed_events[1]
    assert second_session.primary_session_id == 117223
    assert second_session.parent_id == 38385
    assert second_session.title == "Labor Circle"
    assert second_session.location == "Community Church of Boston, 565 Boylston St, Boston, MA 02116, USA"
    assert second_session.event_page_url == "https://bostondsa.solidarity.tech/labor-circle"
    assert second_session.start == datetime(2026, 10, 7, hour=18, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))
    assert second_session.end == datetime(2026, 10, 7, hour=20, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))

def test_translate_recurring_virtual_event():
    pass

def test_translate_recurring_hybrid_event():
    """
    Event in ST has the event parent and then 2 in person sessions and 2 virtual sessions (that correspond to an in person session)
    This should result in 2 calendar event 
    """
    parsed_events = SolidarityTech._translate_event(recurring_hybrid_event)

    assert len(parsed_events) == 2

    first_session = parsed_events[0]
    assert first_session.primary_session_id == 121193
    assert first_session.parent_id == 38999
    assert first_session.title == "Labor Working Group Monthly Meeting"
    assert first_session.location == "TBA and on Zoom https://us02web.zoom.us/j/81053705658?pwd=wnzHDMJspbqUCotjOWnePvQcRAFEVV.1"
    assert first_session.event_page_url == "https://bostondsa.solidarity.tech/labor-working-group-monthly-meeting"
    assert first_session.start == datetime(2026, 11, 18, hour=18, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))
    assert first_session.end == datetime(2026, 11, 18, hour=20, minute=0, second=0, tzinfo=ZoneInfo("America/New_York"))

    second_session = parsed_events[1]
    assert second_session.primary_session_id == 118677
    assert second_session.parent_id == 38999
    assert second_session.title == "Labor Working Group Monthly Meeting"
    assert second_session.location == "https://us02web.zoom.us/j/81053705658?pwd=wnzHDMJspbqUCotjOWnePvQcRAFEVV.1"
    assert second_session.event_page_url == "https://bostondsa.solidarity.tech/labor-working-group-monthly-meeting"
    assert second_session.start == datetime(2026, 10, 21, hour=18, minute=30, second=0, tzinfo=ZoneInfo("America/New_York"))
    assert second_session.end == datetime(2026, 10, 21, hour=20, minute=0, second=0, tzinfo=ZoneInfo("America/New_York"))

def test_translate_events_generator():
    pass