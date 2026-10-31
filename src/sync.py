import argparse
import json
import os
import urllib
from datetime import date
from datetime import datetime
from pprint import pprint

import boto3

from event_connectors.actionnetwork import ActionNetwork
from event_connectors.airtable import Airtable
from event_connectors import SolidarityTech
from event_models import AirtableEvent
from event_differ import EventDiffer

# AWS Clients
SECRETSMANAGER = boto3.client('secretsmanager', region_name='us-east-1')

ACTION_NETWORK_GROUP_KEY_MAP = os.environ.get('ACTION_NETWORK_GROUP_KEY_MAP')
if not ACTION_NETWORK_GROUP_KEY_MAP:
    secret_id = os.environ.get('ACTION_NETWORK_SECRET_ID')
    raw_secret = SECRETSMANAGER.get_secret_value(SecretId=secret_id)
    ACTION_NETWORK_GROUP_KEY_MAP = json.loads(raw_secret['SecretString'])

AIRTABLE_PERSONAL_ACCESS_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
if not AIRTABLE_PERSONAL_ACCESS_TOKEN and not AIRTABLE_BASE_ID:
    secret_id = os.environ['AIRTABLE_SECRET_ID']
    raw_secret = SECRETSMANAGER.get_secret_value(SecretId=secret_id)
    secret = json.loads(raw_secret['SecretString'])
    AIRTABLE_PERSONAL_ACCESS_TOKEN = secret['personal_access_token']
    AIRTABLE_BASE_ID = secret['base_id']


def event_time(time):
    try:
        return datetime.strptime(time['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    except KeyError:
        return datetime.strptime(time['date'], '%Y-%m-%d').date()

def handle_an_events(event, *_):
    # Log Event
    print(f'EVENT {json.dumps(event)}')

    # Get args from event
    event = event or {}
    dryrun = event.get('dryrun') or False
    verbose = event.get('verbose') or False

    actionnetwork_events = []
    for actionnetwork_group, actionnetwork_key in ACTION_NETWORK_GROUP_KEY_MAP.items():
        if not actionnetwork_key: continue  # Skip any keys that have not yet been populated

        print(f"Fetching ActionNetwork events for: {actionnetwork_group}")
        actionnetwork = ActionNetwork(actionnetwork_key)
        actionnetwork_events.extend(actionnetwork.events())

    airtable = Airtable(AIRTABLE_PERSONAL_ACCESS_TOKEN, AIRTABLE_BASE_ID)
    airtable_events = airtable.events()

    differ = EventDiffer(
        events_from_source=actionnetwork_events,
        events_at_destination=airtable_events,
        verbose=verbose
    )
    differ.match_events()

    new_events = differ.events_to_add()

    updated_events = differ.events_to_update()
    changed_events = [e for e in updated_events if not e.removed]
    removed_events = [e for e in updated_events if e.removed]

    if verbose:
        print(f"All events retrieved from ActionNetwork: {actionnetwork_events}")
        print(f"New events: {new_events}")
        print(f"Changed events: {changed_events}")
        print(f"Removed events: {removed_events}")

    print(f"{len(actionnetwork_events)} events retrieved from ActionNetwork")
    print(f"{len(new_events)} new events")
    print(f"{len(changed_events)} changed events")
    print(f"{len(removed_events)} Removed events")

    if not dryrun:
        airtable.add_events(new_events)
        # Cancelled events are marked removed in Airtable by updating them
        airtable.update_events(changed_events + removed_events)

def handle_st_events(event, *_):
    dryrun = event.get('dryrun') or False
    verbose = event.get('verbose') or False

    st = SolidarityTech(os.environ['SOLIDARITY_TECH_ACCESS_TOKEN'])

    max_events = event.get('max_events')
    if max_events is None:
        max_events = 25 if dryrun else None

    generator = st.translate_events(max_events, verbose)

    airtable_events = (event.translate_to(AirtableEvent) for event in generator)

    if dryrun:
        print(f"\n--- [DRYRUN MODE] Simulating Airtable Upsert ---")
        count = 0
        for item in airtable_events:
            count += 1
            print(f"[DRYRUN] Prepared Airtable Event #{count}: {item.raw}")
        print(f"--- [DRYRUN COMPLETE] Successfully simulated {count} records ---\n")
    else:
        airtable = Airtable(AIRTABLE_PERSONAL_ACCESS_TOKEN, AIRTABLE_BASE_ID)
        airtable.upsert_events(airtable_events)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='EventSync',
        description='Syncs events from external platforms (SolidarityTech, ActionNetwork) to Airtable'
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--st', action='store_true', help='Run only SolidarityTech sync')
    group.add_argument('--an', action='store_true', help='Run only ActionNetwork sync')
    
    parser.add_argument('-s', '--sync', action='store_true', help='Execute live sync (default is dry-run)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--max-events', type=int, help='Limit maximum events fetched per source (for testing)')

    args = parser.parse_args()

    event = {
        'dryrun': not args.sync,
        'verbose': args.verbose,
    }
    if args.max_events is not None:
        event['max_events'] = args.max_events

    run_st = args.st or (not args.st and not args.an)
    run_an = args.an or (not args.st and not args.an)

    if run_st:
        if args.verbose:
            print("=== Running SolidarityTech Sync ===")
        try:
            handle_st_events(event)
        except Exception as e:
            print(f"Error in SolidarityTech sync: {e}")
            traceback.print_exc()

    if run_an:
        if args.verbose:
            print("\n=== Running ActionNetwork Sync ===")
        try:
            handle_an_events(event)
        except Exception as e:
            print(f"Error in ActionNetwork sync: {e}")
            traceback.print_exc()
            
    if args.verbose:
        print("\n=== Sync Process Complete ===")