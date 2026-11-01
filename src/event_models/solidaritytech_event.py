from zoneinfo import ZoneInfo

from .event import Event

""" 
While the AN events cannot be recurring, ST events can. 
An Event Series in ST is made of multiple sessions. For adapting to the google calendar 
through Airtable, a SolidarityTechEvent here corresponds to an "event_session" in the ST API. 

NOTE: this is NOT a 1 to 1 relationship! ST has TWO (2) sessions for any event that is 
hybrid (both online and in person). These sessions are combined into one (1) 
SolidarityTechEvent here with both session information. This prevents duplicate entries 
on the calendar for the same meeting.
"""
class SolidarityTechEvent(Event):
    # TODO: we should indicate if the event is part of a series in some way

    PRIMARY_ID_NAME = 'primary_session_id'

    # this handles the translation to Airtable without changing the schema there
    @property
    def actionnetwork_id(self):
        return str(self.primary_session_id)

    @property
    def primary_session_id(self):
        """
        We use the primary session id as the unique identifier for a calendar event
        This ensures recurring events (with multiple sessions) are considered unique for the calendar
        and also handles hybrid events with 2 sessions by using the primary id
        """
        return self.lookup('primary_session_id')

    @property
    def parent_id(self):
        """
        Returns the id of the ST event that is a parent of this session
        """
        return self.lookup('parent_id')

    # this handles the translation to Airtable without changing the schema there
    @property
    def actionnetwork_link(self):
        return self.event_page_url

    @property
    def event_page_url(self):
        return self.lookup('event_page_url')

    @property
    def scope_id(self):
        return self.lookup('scope_id')

    @property
    def scope_type(self):
        # 'Chapter' or 'Organization'
        return self.lookup('scope_type')

    @property
    def title(self):
        return self.lookup('title')

    @property
    def description(self):
        return self.lookup('description')

    # this is on the higher level event as well, doesn't neccessary cascade down
    @property
    def tags(self):
        return (self.lookup('campaign_tags') or []) + (self.lookup('tags') or [])

    @property
    def start(self):
        raw_start = self.lookup('start_time')
        return SolidarityTechEvent.to_datetime(raw_start)

    @property
    def end(self):
        raw_end = self.lookup('end_time')
        return SolidarityTechEvent.to_datetime(raw_end)

    @classmethod
    def to_datetime(cls, raw_time):
        # Solidarity Tech has our start/end time of events in UTC-8 time (idk why)
        # created_at and updated_at are in UTC-7 time
        # I'm converting these to Eastern Time similar to the actionnetwork_event model
        time_with_weird_zone = super().to_datetime(raw_time)
        return time_with_weird_zone.astimezone(ZoneInfo("America/New_York"))

    @property
    def updated_at(self):
        raw_updated_at = self.lookup('updated_at')
        return SolidarityTechEvent.to_datetime(raw_updated_at)

    @property
    def created_at(self):
        raw_created_at = self.lookup('created_at')
        return SolidarityTechEvent.to_datetime(raw_created_at)
    
    @property
    def location(self):
        physical_loc = self.location_address
        virtual_loc = self.location_url
        if physical_loc and virtual_loc:
            return f"{physical_loc} and on Zoom {virtual_loc}"
        elif physical_loc:
            return physical_loc
        else: 
            return virtual_loc

    @property
    def location_address(self):
        if self.event_type != 'virtual':
            if self.lookup('location_name'):
                return f"{self.lookup('location_name')}, {self.lookup('location_address')}"
            else:
                return self.lookup('location_address')
        else:
            return None

    @property
    def location_url(self):
        if self.event_type != 'in_person':
            return self.lookup('virtual_url') or self.lookup('location_address')
        else:
            return None

    @property
    def event_type(self):
        return self.lookup('event_type')

    @property
    def removed(self):
        return False
