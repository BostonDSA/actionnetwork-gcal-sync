from .event import Event
from datetime import datetime, timedelta

class AirtableEvent(Event):
    REQUIRED_FIELD_NAMES = {
        'actionnetwork_id',
        'title',
        'description',
    }
    PRIMARY_ID_NAME = 'airtable_id'

    @property
    def airtable_id(self):
        return self.lookup('id')

    @airtable_id.setter
    def airtable_id(self, airtable_id):
        self.set(airtable_id, 'id')

    @property
    def updated_at(self):
        return self.lookup('fields', 'modified')

    @property
    def actionnetwork_id(self):
        return self.lookup('fields', 'actionnetwork_id')

    @actionnetwork_id.setter
    def actionnetwork_id(self, actionnetwork_id):
        self.set(actionnetwork_id, 'fields',  'actionnetwork_id')

    @property
    def actionnetwork_link(self):
        return self.lookup('fields', 'actionnetwork_link')

    @actionnetwork_link.setter
    def actionnetwork_link(self, actionnetwork_link):
        self.set(actionnetwork_link, 'fields',  'actionnetwork_link')

    @property
    def title(self):
        return self.lookup('fields', 'Event Title')

    @title.setter
    def title(self, title):
        self.set(title, 'fields', 'Event Title')

    @property
    def description(self):
        desc = self.lookup('fields', 'Description')
        # When reading or comparing descriptions, ignore extra whitespace
        # inserted by the Airtable platform
        return desc.strip() if desc else desc

    @description.setter
    def description(self, description):
        # Airtable forums state that long text fields can store up to 100,000
        # characters. Some of our ActionNetwork descriptions exceed this
        # (primarily due to embedded images). For now, simply truncate to fit
        airtable_desc = description[0:50000]
        self.set(airtable_desc, 'fields', 'Description')

    @property
    def host_group(self):
        return self.lookup('fields', 'Host Group')

    @host_group.setter
    def host_group(self, group_name):
        return self.set(group_name, 'fields', 'Host Group')

    @property
    def start(self):
        return AirtableEvent.to_datetime(self.lookup('fields', 'Start Time'))

    @start.setter
    def start(self, start):
        start_str = AirtableEvent.from_datetime(start)
        return self.set(start_str, 'fields', 'Start Time')

    @property
    def end(self):
        return AirtableEvent.to_datetime(self.lookup('fields', 'End Time'))

    @end.setter
    def end(self, end):
        return self.set(AirtableEvent.from_datetime(end), 'fields', 'End Time')

    @classmethod
    def from_datetime(cls, dt):
        # Airtable can accept formatted date strings including timezone.
        # Our Airtable date columns are formatted to use eastern time, and
        # any values will be converted accordingly. As long as the source
        # uses eastern time, these will compare consistently
        return dt.isoformat()

    @property
    def location(self):
        return self.lookup('fields', 'Location')

    @location.setter
    def location(self, location):
        return self.set(location, 'fields', 'Location')

    @property
    def removed(self):
        return bool(self.lookup('fields', 'removed'))

    @removed.setter
    def removed(self, removed):
        self.set(removed, 'fields', 'removed')
