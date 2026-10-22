import requests

url = "https://api.solidarity.tech/v1/events?_limit=20&_offset=0&_since=0"

headers = {"authorization": "Bearer " + os.environ['SOLIDARITY_TECH_ACCESS_TOKEN'] }
response = requests.get(url, headers: headers)
print(response.text)

# class SolidarityTech():
#     def __init__(self, api_key):
#         self.api_key = api_key


event = {
    'id': 1,
    'title': 'Event title',
    "scope_id": 3061,
    "scope_type": "Chapter",
    "event_type": "in_person",
    "location_name": null,
    "location_data": null,
    "tags": [
        "New Member Friendly",
        "canvass",
        "Canvasses",
        "MetroWest"
    ],
    "campaign_tags": [
        "No on 5"
    ],
    "event_sessions": [ ]
    "event_page_url": "https://bostondsa.solidarity.tech/no-on-5-canvass-copy",
    "description": "We will be meeting at the corner of East Central st. &amp; North Main St. to canvass door to door for the \"No on 5\" campaign. Expect to canvass from 5:30 to around 8pm, and wear warm clothes for when the sun goes down. No canvassing experience necessary! Talking points and a brief training will be provided.",
    "hide_address_until_rsvp": false,
    "show_in_web_calendars": true,
    "accessibility_info": null,
    "primary_event_id": 1,
    "is_co_hosted_mirror": false,
    "internal_co_host_chapters": [],
    "created_at": "2026-10-16T16:44:00.261-07:00"
}

session_in_person = {
    "id": 133550,
    "mobilize_event_id": 44782,
    "start_time": "2026-10-23T14:00:00.000-07:00",
    "end_time": "2026-10-23T17:00:00.000-07:00",
    "title": "\"No On 5\" Canvass",
    "created_at": "2026-10-16T16:44:00.273-07:00",
    "updated_at": "2026-10-16T16:48:23.116-07:00",
    "location_name": "Newton Center",
    "location_data": {
    "components": [
        {
        "long_name": "Centre Street & Beacon Street",
        "short_name": "Centre St & Beacon St",
        "types": [
            "intersection"
        ]
        },
        {
        "long_name": "Newton Centre",
        "short_name": "Newton Centre",
        "types": [
            "neighborhood",
            "political"
        ]
        },
        {
        "long_name": "Newton",
        "short_name": "Newton",
        "types": [
            "locality",
            "political"
        ]
        },
        {
        "long_name": "Middlesex County",
        "short_name": "Middlesex County",
        "types": [
            "administrative_area_level_2",
            "political"
        ]
        },
        {
        "long_name": "Massachusetts",
        "short_name": "MA",
        "types": [
            "administrative_area_level_1",
            "political"
        ]
        },
        {
        "long_name": "United States",
        "short_name": "US",
        "types": [
            "country",
            "political"
        ]
        },
        {
        "long_name": "02459",
        "short_name": "02459",
        "types": [
            "postal_code"
        ]
        }
    ],
    "coordinates": {
        "lat": 42.3299966,
        "lng": -71.1948805
    },
    "address_city": "Newton",
    "full_address": "Centre St & Beacon St, Newton, MA 02459, USA",
    "address_state": "MA",
    "address_line_1": "Centre Street & Beacon Street",
    "address_country": "US",
    "address_postal_code": "02459"
    },
    "lonlat": "POINT (-71.1948805 42.3299966)",
    "location_address": "Centre St & Beacon St, Newton, MA 02459, USA",
    "show_rsvp_bar": true,
    "show_title_in_form": false,
    "max_capacity": 0,
    "note": "We will be meeting at the corner of Beacon st. & Centre St. to canvass for the \"No on 5\" campaign. No experience necessary! Come early to support CD4 constituents in their 4-5pm standout for Palestine!",
    "tags": [
    "New Member Friendly",
    "canvass",
    "Canvasses",
    "MetroWest",
    "Electoral Organizing Committee"
    ],
    "zoom_account_id": null,
    "zoom_meeting_id": null,
    "zoom_meeting_data": null,
    "event_type": "in_person",
    "primary_session_id": 133550,
}

session_virtual = {
    "id": 132126,
    "mobilize_event_id": 43905,
    "start_time": "2026-11-02T15:00:00.000-08:00",
    "end_time": "2026-11-02T16:55:00.000-08:00",
    "title": "Solidarity Tech office hours",
    "created_at": "2026-10-15T06:46:56.010-07:00",
    "updated_at": "2026-10-15T08:40:08.385-07:00",
    "location_name": null,
    "location_data": null,
    "lonlat": null,
    "location_address": "https://us02web.zoom.us/meeting/register/j7GSTW84S8O7RVGiCanvlg",
    "tags": [],
    "zoom_account_id": 419,
    "zoom_meeting_id": "81187768390",
    "zoom_meeting_data": {
        "id": 81187768390,
        "type": 2,
        "uuid": "tn1+IKo+TAGdOgLqNW/+gw==",
        "topic": "Solidarity Tech office hours",
        "status": "waiting",
        "host_id": "seMiINYmTnikKKlyuH4P1g",
        "duration": 120,
        "join_url": "https://us02web.zoom.us/j/81187768390?pwd=XdjQL2RKGO0usBYXxbC4b9X80bPKaP.1",
        "password": "825303",
        "settings": {} # not important
        "timezone": "America/New_York",
        "start_url": "https://us02web.zoom.us/s/81187768390?zak=eyJ0eXAiOiJKV1QiLCJzdiI6IjAwMDAwMiIsInptX3NrbSI6InptX28ybSIsImFsZyI6IkhTMjU2In0.eyJpc3MiOiJ3ZWIiLCJjbHQiOjAsIm1udW0iOiI4MTE4Nzc2ODM5MCIsImF1ZCI6ImNsaWVudHNtIiwidWlkIjoic2VNaUlOWW1UbmlrS0tseXVINFAxZyIsInppZCI6Ijg3NmE3Njg4MGQ4ODRjZTU4ODljNWU2MGQzMDQ0NWNhIiwic2siOiI0ODQyMjE0MjA3ODI5MTEwNDMyIiwic3R5IjoxMDAsIndjZCI6InVzMDIiLCJleHAiOjE3OTIwNzkyMTYsImlhdCI6MTc5MjA3MjAxNiwiYWlkIjoiVWNuNW84VHdRYkNyVVFpMzFpV0laZyIsImNpZCI6IiJ9.eR-BghZSAjh7nWZXiSuHhScoZPaRfIOBgcNi2_gJaVo",
        "created_at": "2026-10-15T13:46:56Z",
        "host_email": "info@bostondsa.org",
        "start_time": "2026-11-17T23:00:00Z",
        "pre_schedule": false,
        "chat_join_url": "https://us02web.zoom.us/launch/jc/81187768390",
        "h323_password": "825303",
        "pstn_password": "825303",
        "creation_source": "open_api",
        "registration_url": "https://us02web.zoom.us/meeting/register/j7GSTW84S8O7RVGiCanvlg",
        "encrypted_password": "XdjQL2RKGO0usBYXxbC4b9X80bPKaP.1"
    },
    "event_type": "virtual",
}

# when there is a hybrid meeting, solidarity tech has 2 sessions for it. one has physical location and one has zoom information
# maybe we determine an event is the same when the following are the same:
#   - mobilize_event_id # this is the parent event, this will match for recurring events too
#   - title # I think these should match in this case
#   - start_time 
#   - end_time 
# the paired_meci_id seems to pair the events together actually hold on

