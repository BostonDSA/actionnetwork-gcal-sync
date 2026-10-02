import json
import requests
import requests_mock
from urllib.parse import urlparse, parse_qs
import unittest.mock as mock
from datetime import datetime
from event_connectors import ActionNetwork


AN_URL = 'https://actionnetwork.org/api/v2/'
AN_EVENTS_URL = f'{AN_URL}events'

def fake_get(request, context, action_network_events):
    context.status_code = 200
    req_url = urlparse(request.url)
    
    query_params = parse_qs(req_url.query)
    page = int(query_params.get('page', [1])[0])
    
    return { 
        'total_pages': len(action_network_events),
        'page': page,
        '_links': {
        'next': {
            'href': 'https://actionnetwork.org/api/v2/events?page=2'
        }
        },
            '_embedded': {
                'osdi:events': [ action_network_events[page - 1] ]
            } 
        }

'''
This test mocks the AN network calls we make to read events. 
'''
def test_actionnetwork(action_network_events):
    with requests_mock.Mocker() as mock:
        # mock the api key get request
        mock.get(AN_URL, json={"motd":"Welcome to the Action Network OSDI API v2 Entry Point!", "_links": {"self":{"title":"This API entry point","href":"https://actionnetwork.org/api/v2/"},"osdi:events":{"title":"The collection of events in the system","href":"https://actionnetwork.org/api/v2/events"},"max_page_size":25,"vendor_name":"Action Network","product_name":"Action Network","namespace":"action_network","osdi_version":"1.1.1"} })

        # mock the event get request
        mock.get(AN_EVENTS_URL, json=lambda req, ctx: fake_get(req, ctx, action_network_events))

        an = ActionNetwork('fake-api-key')

        events = an.events() # min_creation_time='2018-01-01T00:00:00Z'
        assert len(events) == 2
        
        event_1 = events[0]
        assert event_1.title == "My first event!"

