import requests
import os

from collections.abc import Iterator
from datetime import datetime, timezone, timedelta

from event_models import SolidarityTechEvent

class SolidarityTech():
    def __init__(self, api_key):
        self.api_key = api_key

    @property
    def _headers(self):
        return { "authorization": "Bearer " + self.api_key }


    def _fetch_page(self, session, offset, limit):
        """
        Pulls the first page of events from Solidarity Tech
        """
        # _since is UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
        # I THINK this is looking at events that have been created/updated since the UTC time??
        # TODO: this could be useful in reducing the number of events we have to look through
        since = 0 # (datetime.now(timezone.utc) - timedelta(hours=24)).timestamp
        url = f"https://api.solidarity.tech/v1/events?_limit={limit}&_offset={offset}&_since={since}"
        
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            payload = response.json()
            return payload.get("data", [])
        except requests.exceptions.RequestException as err:
            print(f"API request failed at offset {offset}: {err}")
            return []


    def fetch_events(self) -> Iterator[dict[str, any]]:
        """
        A generator that yields SolidarityTech events by page from the API
        """
        session = requests.Session()
        session.headers.update(self._headers)
        
        offset = 0
        limit = 100 # max allowed by the API
        while True:
            items = self._fetch_page(session, offset, limit)
            
            # If the page is empty (or an error occurred returning []), stop the generator
            if not items:
                break
            
            for item in items:
                yield item
                
            # We've reached the last page
            if len(items) < limit:
                break
            
            offset += limit

    @classmethod
    def _translate_event(self, event: dict[str, any]) -> list[SolidarityTechEvent]:
        """
        Solidarity Tech "events" are the parent of "sessions". This allows them to have recurring and hybrid events (with multiple locations).
        Since we want calendar compatible events, this method converts a raw ST event -> SolidarityTechEvent[]
        When there is a recurring event, we will return multiple calendar events
        When there is a hybrid event, that will be combined from 2 sessions into 1
        """

        shared_info = {
            'event_page_url': event['event_page_url'],
            'parent_id': event['id'],
            'scope_id': event['scope_id'],
            'scope_type': event['scope_type'],
            'title': event['title'],
            'description': event['description']
        }

        session_map = {session["id"]: session for session in event['event_sessions']}
    
        processed_ids = set()
        combined_events = []

        for session in event['event_sessions']:
    
            session_id = session["id"]
            
            if session_id in processed_ids:
                continue
                
            paired_id = session.get("paired_meci_id")
            
            if paired_id and paired_id in session_map and paired_id not in processed_ids:
                partner_session = session_map[paired_id]
                
                # Mark both as processed so we don't duplicate them
                processed_ids.add(session_id)
                processed_ids.add(paired_id)
                
                hybrid_event_info = merge_paired_sessions(session, partner_session)
                
                combined_events.append(SolidarityTechEvent({**hybrid_event_info, **shared_info}))

            else:
                # Standalone session
                processed_ids.add(session_id)
                session_info = {**session, **shared_info}
                combined_events.append(SolidarityTechEvent(session_info))
                
        return combined_events


    def merge_paired_sessions(session_a: dict[str, any], session_b: dict[str, any]) -> dict[str, any]:
        """
        Merges a virtual and in-person session into a single hybrid calendar event.
        """
        virtual_session = session_a if session_a["event_type"] == "virtual" else session_b
        in_person_session = session_a if session_a["event_type"] == "in_person" else session_b
  
        # Create a unified hybrid record
        merged = virtual_session.copy()
        merged["event_type"] = "hybrid"
        merged["location_address"] = in_person_session.get("location_address") # Physical location
        merged["virtual_url"] = virtual_session.get("location_address")        # Zoom link
        
        return merged


    def translate_events(self) -> Iterator[SolidarityTechEvent]:
        api_gen = self.fetch_events()
        for raw_event in api_gen:
            translated_events_list = SolidarityTech._translate_event(raw_event)
            yield from translated_events_list
