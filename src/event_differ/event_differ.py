from event_models import AirtableEvent

class EventDiffer():
    """Computes the difference between sets of events of different classes.

    EventDiffer produces change sets, or event lists which, if applied to the
    'destination' system, will bring its' event store into sync with the
    'source' list.

    Note: We differentiate the lists of events, and the classes of those events,
    by 'source' vs. 'destination'. While these event lists could be arbitrary,
    these names mirror our main use-case where the event lists/classes reflect
    the state of events stored in 3rd party systems. The names also the
    direction we compute the diff in - we are computing the diff relative to
    the existing events in the 'destination' list.
    """
    def __init__(
        self,
        events_from_source,
        events_at_destination,
        destination_class=AirtableEvent,
        verbose=False
    ):
        """Create an EventDiffer.

        :param events_from_source: list of events to generate the diff for
        :type events_from_source: List[Event]
        :param events_at_destination: the baseline events to compare against
        :type events_at_destination: List[Event]
        :param destination_class: The class to build new destination events
            with, in case there are no existing destination events to match
            against. defaults to AirtableEvent
        :type destination_class: class, optional
        :param verbose: Whether to print detailed information about the
            calculated changes. defaults to False
        :type verbose: boolean, optional
        """
        self.verbose = verbose

        self.events_from_source = events_from_source
        self.source_class = self._event_class(events_from_source)

        self.events_at_destination = events_at_destination
        if events_at_destination:
            self.destination_class = self._event_class(events_at_destination)
        else:
            self.destination_class = destination_class

        # We expect that the destination events store the primary ID value from
        # the source events as a common ID that can be used to compare events
        self.common_id_name = self.source_class.PRIMARY_ID_NAME

    @staticmethod
    def _event_class(events):
        """Determine the event type for a list of events.

        :param events: list of events to evaluate
        :type events: List[Event]
        :raises ValueError: if there are multiple event types found
        :return: the type of the events
        :rtype: class
        """
        unique_types = {e.__class__ for e in events}
        if len(unique_types) > 1:
            raise ValueError(
                "Expected a single event class per event list - multiple found"
            )
        return unique_types.pop()

    def _events_by_common_id(self, events):
        return {
            getattr(e, self.common_id_name): e
            for e in events
            # Ignore events with no common ID value
            # (such as events entered manually into the destination system)
            if getattr(e, self.common_id_name) is not None
        }

    def match_events(self):
        """Match up events across the source and destination systems and
        store in instance variables.

        Must be run before accessing the change sets (events_to_add, etc).
        """
        source_events = self._events_by_common_id(self.events_from_source)
        dest_events = self._events_by_common_id(self.events_at_destination)

        not_in_destination = []
        present_in_both = []
        for common_id, source_event in source_events.items():
            if common_id in dest_events:
                dest_event = dest_events.pop(common_id)
                present_in_both.append([dest_event, source_event])
            else:
                not_in_destination.append(source_event)

        self.new_source_events = not_in_destination
        self.matching_source_dest_event_pairs = present_in_both

        if list(dest_events.values()):
            print(
                "WARNING: Events exist at the destination but are not "
                f"present in the source: {dest_events}"
            )

    def events_to_add(self):
        """Events that do not exist in the destination and can be added to
        bring it into alignment with the source.

        :return: list of destination-type events
        """
        return [
            source_event.translate_to(self.destination_class)
            for source_event in self.new_source_events
        ]

    def events_to_update(self):
        """Events that exist in both the source and destination and can be
        updated in the destination to bring it into alignment with the source.

        :return: list of destination-type events
        """
        events_to_update = []
        for dest_event, source_event in self.matching_source_dest_event_pairs:
            event = source_event.translate_to(self.destination_class)
            event.primary_id = dest_event.primary_id
            if dest_event != event:
                if self.verbose: dest_event.print_diff(event)
                events_to_update.append(event)
        return events_to_update
