import requests_mock

from pyairtable import Api

from event_connectors import Airtable

access_token = "fake_access_token"
base_id = "fake_base_id"
table_name = "Events"

def test_airtable(airtable_events):

    api = Api(access_token)
    table = api.table(base_id, table_name)

    airtable_connector = Airtable(access_token, base_id)
    airtable_connector.base._api = api

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    mock_response = {
        "records": airtable_events
    }

    with requests_mock.Mocker() as mock:
        mock.get(url, json=mock_response)

        records = airtable_connector.events()

        assert len(records) == 2
        assert mock.called

        event_1 = records[0]
        
        assert event_1.title == "My first event!"
