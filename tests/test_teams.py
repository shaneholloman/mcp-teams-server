import pytest
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter
from botframework.connector.auth import ManagedIdentityAppCredentials

from mcp_teams_server import TeamsClient
import os
import logging
import sys
from dotenv import load_dotenv

APP_ID = os.environ.get("TEAMS_APP_ID")
APP_TENANT_ID = os.environ.get("TEAMS_APP_TENANT_ID")
TEAMS_ID = os.environ.get("TEAMS_CHANNEL_ID")
TEAMS_TENANT_ID = os.getenv("TEAMS_APP_TENANT_ID")

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

@pytest.fixture()
def setup_teams_client() -> TeamsClient:
    settings = BotFrameworkAdapterSettings(
        app_id=APP_ID,
        app_credentials=ManagedIdentityAppCredentials(app_id=APP_ID)
    )
    adapter = BotFrameworkAdapter(settings)
    return TeamsClient(adapter, TEAMS_ID, TEAMS_TENANT_ID)


def test_get_team_id(setup_teams_client):
    print(f'Teams Client TEAM_ID: {setup_teams_client.team_id}')
    assert True

@pytest.mark.asyncio
async def test_list_channels(setup_teams_client):
    print(f'Teams Client TEAM_ID: {setup_teams_client.team_id}')
    result = await setup_teams_client.list_channels()
    print(f'Result {result}')
    assert True

@pytest.mark.asyncio
async def test_start_thread(setup_teams_client):
    print(f'Teams Client TEAM_ID: {setup_teams_client.team_id}')
    channel_id = os.getenv("TEAMS_CHANNEL_ID")
    result = await setup_teams_client.start_thread(channel_id, "First thread", "First thread content")
    print(f'Result {result}')
