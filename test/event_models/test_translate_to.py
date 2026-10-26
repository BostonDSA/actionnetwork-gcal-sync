from test.data.solidarity_tech_events import (
    single_in_person_event,
    single_virtual_event,
    recurring_in_person_event,
    recurring_virtual_event,
    recurring_hybrid_event,
)
from event_connectors import SolidarityTech
from event_models import AirtableEvent


def test_translate_st_to_at():
    parsed_events = SolidarityTech._translate_event(single_in_person_event)
    assert len(parsed_events) == 1

    st_event = parsed_events[0]
    at_event = st_event.translate_to(AirtableEvent)

    assert at_event.actionnetwork_id == st_event.primary_session_id
    assert at_event.title == st_event.title
    assert at_event.location == st_event.location

