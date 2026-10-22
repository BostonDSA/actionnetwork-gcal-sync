from .event import Event
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

class ActionNetworkEvent(Event):
    PRIMARY_ID_NAME = 'actionnetwork_id'

    @property
    def actionnetwork_id(self):
        for identifier in self.lookup('identifiers'):
            if identifier.startswith('action_network:'):
                return identifier[len('action_network:'):]

    @property
    def actionnetwork_link(self):
        return self.lookup('browser_url')

    @property
    def updated_at(self):
        return self.lookup('modified_date')

    @property
    def title(self):
        return self.lookup('title')

    @property
    def description(self):
        return self.lookup('description')

    # TODO: not in the api docs..
    @property
    def host_group(self):
        return self.lookup('action_network:sponsor', 'title')

    @property
    def start(self):
        raw_start = self.lookup('start_date')
        return ActionNetworkEvent.to_datetime(raw_start)

    @property
    def end(self):
        raw_end = self.lookup('end_date')
        if raw_end is None:
            end = self.start + timedelta(hours=1)
        else:
            end = ActionNetworkEvent.to_datetime(raw_end)
        return end

    @classmethod
    def to_datetime(cls, raw_time):
        # ActionNetwork gives us time strings that are encoded as UTC but
        # are actually naieve time (exactly as the user entered). We assume
        # that the user wanted eastern time - If this turns out to be
        # unreliable, we can look into deriving timezone from location.
        # If an event is virtual (no location) ActionNetwork requires the
        # user to enter a timezone manually, but this does not seem to
        # appear in the API response, so we treat it the same way.
        time_with_utc_zone = super().to_datetime(raw_time)
        return time_with_utc_zone.replace(tzinfo=ZoneInfo("America/New_York"))

    @property
    def location(self):
        loc = self.lookup('location')

        venue = loc['venue'] if 'venue' in loc else ''
        addr = ' '.join(loc['address_lines']) if 'address_lines' in loc else ''
        city = loc['locality'] if 'locality' in loc else ''
        state = loc['region'] if 'region' in loc else ''
        zipcode = loc['postal_code'] if 'postal_code' in loc else ''

        # Only include parts of the address that have non-whitespace content.
        # Sometimes, hosts enter just the venue title such as 'Zoom' or
        # 'City Hall'
        str_loc = ", ".join([
            part for part in [venue, addr, f'{city} {state}', zipcode]
            if part.strip()
        ])

        # There is no flag that indicates the event is online.
        # Online events seemed to have the same lat/long, so we tried using that,
        # but it wasn't always true, so some of our online event locations were empty.
        # Instead we'll try checking if they have no address.
        if not str_loc: str_loc = 'Online'

        return str_loc

    @property
    def removed(self):
        return self.lookup('status') == 'cancelled'
