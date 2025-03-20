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
        logging.StreamHandler(sys.stderr)
    ]
)

LOGGER = logging.getLogger(__name__)

@pytest.fixture()
def setup_teams_client() -> TeamsClient:
    # Cloud adapter
    config = BotConfiguration()
    adapter = CloudAdapter(ConfigurationBotFrameworkAuthentication(config, logger=LOGGER))

    # Graph client
    credentials = ClientSecretCredential(
        config.APP_TENANTID,
        config.GRAPH_CLIENT_ID,
        config.GRAPH_CLIENT_SECRET
    )
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credentials=credentials, scopes=scopes)

    return TeamsClient(adapter, graph_client, config.APP_ID, config.APP_TENANTID, config.TEAMS_CHANNEL_ID)

@pytest.mark.asyncio
async def test_start_thread(setup_teams_client):
    LOGGER.info(f'test_start_thread in team: {setup_teams_client.team_id} and channel {setup_teams_client.teams_channel_id}')
    result = await setup_teams_client.start_thread("First thread", "First thread content")
    LOGGER.info(f'Result {result}')
    assert result is not None

@pytest.mark.asyncio
async def test_update_thread(setup_teams_client):
    # TODO: setup test data
    thread_id = ""
    result = await setup_teams_client.update_thread(thread_id, "Thread updated content")
    assert result is not None

@pytest.mark.asyncio
async def test_mention_user(setup_teams_client):
    # TODO: setup test data
    thread_id = ""
    user_id = ""
    result = await setup_teams_client.mention_user(thread_id, user_id, "User mentioned")
    LOGGER.info(f'Result {result}')
    assert result is not None

@pytest.mark.asyncio
async def test_add_reaction(setup_teams_client):
    message_id = ""
    reaction = ""
    result = await setup_teams_client.add_reaction(message_id, reaction)
    LOGGER.info(f'Result {result}')
    assert result is not None

@pytest.mark.asyncio
async def test_read_thread(setup_teams_client):
    # TODO: setup test data
    thread_id = ""
    result = await setup_teams_client.read_thread(thread_id)
    LOGGER.info(f'Result {result}')
    assert result is not None

@pytest.mark.asyncio
async def test_list_members(setup_teams_client):
    # TODO: setup test data
    result = await setup_teams_client.list_members()
    LOGGER.info(f'Result {result}')
    assert result is not None



