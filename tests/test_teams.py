import os

import pytest
from azure.identity.aio import ClientSecretCredential

from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from msgraph import GraphServiceClient

from mcp_teams_server.config import BotConfiguration
from mcp_teams_server.teams import TeamsClient

import logging
import sys
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

LOGGER = logging.getLogger(__name__)

@pytest.mark.integration
@pytest.fixture()
def setup_teams_client() -> TeamsClient:
    # Cloud adapter
    config = BotConfiguration()
    adapter = CloudAdapter(ConfigurationBotFrameworkAuthentication(config, logger=LOGGER))

    # Graph client
    credentials = ClientSecretCredential(
        config.APP_TENANTID,
        config.APP_ID,
        config.APP_PASSWORD
    )
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credentials=credentials, scopes=scopes)

    return TeamsClient(adapter, graph_client, config.APP_ID, config.TEAM_ID, config.TEAMS_CHANNEL_ID)

@pytest.fixture()
def thread_id() -> str:
    return os.environ.get("TEST_THREAD_ID")

@pytest.fixture()
def message_id() -> str:
    return os.environ.get("TEST_MESSAGE_ID")

@pytest.fixture()
def user_name() -> str:
    return os.environ.get("TEST_USER_NAME")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_start_thread(setup_teams_client, user_name):
    LOGGER.info(f'test_start_thread in team: {setup_teams_client.team_id} and channel {setup_teams_client.teams_channel_id}')
    result = await setup_teams_client.start_thread("First thread", "First thread content with mention", user_name)
    print(f'Result {result}\n')
    assert result is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_read_threads(setup_teams_client):
    result = await setup_teams_client.read_threads(50)
    print(f'Result {result}\n')
    assert result is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_thread(setup_teams_client, thread_id, user_name):
    result = await setup_teams_client.update_thread(thread_id, "Thread updated content with mention", user_name)
    print(f'Result {result}\n')
    assert result is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_read_thread_replies(setup_teams_client, thread_id):
    result = await setup_teams_client.read_thread_replies(thread_id, 0, 50)
    print(f'Result {result}\n')
    assert result is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_members(setup_teams_client):
    result = await setup_teams_client.list_members()
    print(f'Result {result}\n')
    assert result is not None



