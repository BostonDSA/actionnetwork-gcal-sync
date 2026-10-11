from event_models import EventDiffer, AirtableEvent, ActionNetworkEvent

EMPTY_AN_LOCATION = {
    "address_lines": [],
    "locality": "",
    "region": "",
    "country": "",
}

base_event_1 = {
    "id": "event_1",
    "title": "Zoom meeting!",
    "desc": "Come chat on zoom with us.",
    "start_time": "2026-01-20T00:00:00Z"
}

def test_event_differ_an_to_airtable_cancelled():

    at_event_1 = AirtableEvent({
        "id": base_event_1["id"],
        "createdTime": "2026-01-01T00:00:00Z",
        "fields": {
            "actionnetwork_id": base_event_1["id"],
            "Event Title": base_event_1["title"],
            "Description": base_event_1["desc"],
            "Start Time": base_event_1["start_time"],
            "Location": "Online",
            "removed": False
        }
    })

    an_event_1 = ActionNetworkEvent({
        "identifiers": [ f"action_network:{base_event_1['id']}" ],
        "origin_system": "Action Network",
        "title": base_event_1["title"],
        "description": base_event_1["desc"],
        "start_date": base_event_1["start_time"],
        "location": EMPTY_AN_LOCATION,
        "status": "cancelled" # this is what the test will be updating
    })
    

    # ActionNetwork events are the ones we are checking for updates
    an_events = [an_event_1]

    # airtable events is the dataset we are comparing to with the goal being to update these
    airtable_events = [at_event_1]

    differ = EventDiffer(an_events, airtable_events, AirtableEvent)

    differ.match_events()

    new_events = differ.events_to_add()

    updated_events = differ.events_to_update()
    changed_events = [e for e in updated_events if not e.removed]
    removed_events = [e for e in updated_events if e.removed]

    assert len(new_events) == 0
    assert len(updated_events) == 1
    assert len(changed_events) == 0
    assert len(removed_events) == 1

    assert removed_events[0].title == base_event_1["title"]

