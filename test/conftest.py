import json
from pathlib import Path
import pytest

@pytest.fixture
def action_network_events():
    fixture_path = Path(__file__).resolve().parent / "data" / "example_action_network_events.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def airtable_events():
    fixture_path = Path(__file__).resolve().parent / "data" / "example_airtable_events.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)