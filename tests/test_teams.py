import pytest
from azure.identity.aio import ClientSecretCredential

from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication

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
    print(f'Teams Client TEAM_ID: {setup_teams_client.team_id}')
    result = await setup_teams_client.start_thread("First thread", "First thread content")
    print(f'Result {result}')
