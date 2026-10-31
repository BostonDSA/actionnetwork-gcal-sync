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
from event_differ import EventDiffer

# AWS Clients
SECRETSMANAGER = boto3.client('secretsmanager')
SNS = boto3.client('sns')

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'ActionNetwork',
                    description = 'Syncs events from ActionNetwork to Airtable')
    parser.add_argument('-s', '--sync', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    handle_an_events({
        'dryrun': not args.sync,
        'verbose': args.verbose,
    })
