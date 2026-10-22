from abc import ABC
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Event(ABC):
    """Abstract base class for Event types.

    Event types provide a standardized interface for accessing common event
    attributes on top of the raw event format as defined by the various event
    systems' APIs.

    Event types do not need to implement every event attribute or property;
    they can be expanded as necessary for their application. However, each type
    should only define common event properties that can be interchanged with
    those of other event types.
    """

    # Collection of names of fields which must be set on the event object
    # in order for it to be valid for pushing to the API for this event type
    REQUIRED_FIELD_NAMES = set()

    # Collection of names of fields which are computed by the event system
    # and therefor should not be pushed via the API
    DERIVED_FIELD_NAMES = {
        'updated_at',
    }

    # The name of the field to use as the primary ID for this event type
    PRIMARY_ID_NAME = None

    def __init__(self, raw_event=None):
        """Create an empty Event object, or create an Event representation of
        raw event info.

        :param dict raw_event: The event info dictionary in raw format (as
            pulled from the respective events service API), defaults to None
        :type raw_event: dict, optional
        """
        if raw_event:
            self.raw = raw_event
        else:
            self.raw = {}

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.event_info() == other.event_info()
        )

    def __repr__(self):
        primary_id = getattr(self, self.PRIMARY_ID_NAME)
        return super().__repr__().replace(
            "object", f"{primary_id}|'{self.title}'"
        )

    def print_diff(self, other):
        print(f"\nDifferences in Event: {self}")
        for field in self.event_fields().union(other.event_fields()):
            self_value = self.event_info()[field]
            other_value = other.event_info()[field]
            if self_value != other_value:
                print(f"Field {field}: {self_value} >> {other_value}")

    @property
    def primary_id(self):
        return getattr(self, self.PRIMARY_ID_NAME)

    @primary_id.setter
    def primary_id(self, value):
        if self.primary_id is not None: raise "Cannot change Primary ID."
        return setattr(self, self.PRIMARY_ID_NAME, value)

    def lookup(self, *keys):
        """A null-safe lookup to find nested attributes in the raw event.

        :params str keys: keys indicating a location to look up in the raw
            event. Each successive key will index into a nested dictionary.
        :return: The value at the given location, or None if no such value
            exists or if the key at any intermediary stage does not exist.
        """
        value = self.raw
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break
        return value

    def set(self, value, *keys):
        """Sets a value in the raw event data.

        :param object value: The value to set.
        :params str keys: keys indicating a location to store the value in the
            raw event. Each successive key will index into a nested dictionary.
        """
        if len(keys) == 0:
            return

        parent_location = self.raw
        for key in keys[:-1]:
            if key not in parent_location:
                parent_location[key] = {}
            parent_location = parent_location[key]

        parent_location[keys[-1]] = value

    @classmethod
    def build(cls, fields):
        """Construct a new event with the given field values.

        :param fields: mapping of field names to field values that the new
            event will be built with
        :type fields: dict
        :raises ValueError: if required fields are not given.
        :return: A new event object with all given fields set.
        :rtype: Event
        """
        missing_fields = cls.REQUIRED_FIELD_NAMES - fields.keys()
        if missing_fields:
            raise ValueError(f"REQUIRED_FIELD_NAMES missing: {missing_fields}")

        new_event = cls()
        for field, value in fields.items():
            if hasattr(new_event, field):
                setattr(new_event, field, value)
            else:
                print(f"Warning: {field} not present in {cls}")
        return new_event

    @classmethod
    def event_fields(cls):
        """Get the names of all properties containing information about the
        event.

        :return: set of property names
        :rtype: set
        """
        return set(dir(cls)) - set(dir(Event)) - cls.DERIVED_FIELD_NAMES

    def event_info(self):
        """Get the names and values of all properties containing information
        about the event record itself.

        :return: dictionary of event information
        :rtype: dict
        """
        return {
            field: getattr(self, field)
            for field in self.__class__.event_fields()
        }

    def translate_to(self, new_class):
        """Translate the event object to a different event format.

        :param new_class: the Event class to translate the event into
        :type new_class: class of Event
        :return: new event with all fields carried over (as  permitted)
        :rtype: Event
        """
        return new_class.build(self.event_info())

    @classmethod
    def to_datetime(cls, raw_time):
        """Translates an event type's native time format into a python datetime.

        :param raw_time: an object representing a time value, in whatever format
            the event type uses to store time values
        :return: a python datetime object representing the same time
        :rtype: datetime
        """
        # This function must be null-safe because raw_time will be None if
        # we are creating the object from scratch.
        if raw_time is None:
            dt = None
        # ActionNetwork and Airtable both appear to give us times as ISO
        # formatted strings, so use this as the default read behavior
        else:
            dt = datetime.fromisoformat(raw_time)
        return dt

    @classmethod
    def from_datetime(cls, dt):
        """Translates a datetime into the event type's native time format.

        We define helpers in the base Event class to prevent the subclass
        helpers from being counted in event_fields

        :param dt: a python datetime object representing a time
        :return: an object representing a time value, in whatever format
            the event type uses to store time values
        """
        raise NotImplementedError
