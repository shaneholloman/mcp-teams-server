from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib import metadata
from typing import AsyncIterator, List, Dict
from pydantic import Field

from azure.identity.aio import ClientSecretCredential
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from mcp.server.fastmcp import FastMCP, Context
from msgraph import GraphServiceClient

from .config import BotConfiguration
from .teams import TeamsClient, TeamsMessage, TeamsThread, TeamsMember
import sys
import logging
from dotenv import load_dotenv

try:
    __version__ = metadata.version("mcp-teams-server")
except metadata.PackageNotFoundError:
    __version__ = "unknown"

# Load .env
load_dotenv()

# Config logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('mcp_teams_server.log')
    ]
)

LOGGER = logging.getLogger(__name__)


@dataclass
class AppContext:
    client: TeamsClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""

    # Bot adapter construction
    bot_config = BotConfiguration()
    adapter = CloudAdapter(ConfigurationBotFrameworkAuthentication(bot_config))

    # Graph client construction
    credentials = ClientSecretCredential(
        bot_config.APP_TENANTID,
        bot_config.GRAPH_CLIENT_ID,
        bot_config.GRAPH_CLIENT_SECRET
    )
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credentials=credentials, scopes=scopes)

    client = TeamsClient(adapter, graph_client, bot_config.APP_ID, bot_config.TEAM_ID, bot_config.TEAMS_CHANNEL_ID)
    yield AppContext(client=client)


mcp = FastMCP("mcp-teams-server", lifespan=app_lifespan)


@mcp.tool(name="teams_greeting", description="Says a hello message from MCP Teams Server")
def teams_greeting(ctx: Context) -> str:
    """Says a hello message from MCP Teams Server"""
    client = ctx.request_context.lifespan_context["client"]
    return f'Hello from mcp-teams-server: {__version__} in team {client.get_team_tenant_id()}!'


@mcp.tool(name="start_thread", description="Start a new thread with a given title and content")
def start_thread(ctx: Context, title: str = Field(description="The new thread title"),
                 content: str = Field(description="The new thread content")) -> TeamsThread:
    client = ctx.request_context.lifespan_context["client"]
    return client.start_thread(title, content)


@mcp.tool(name="update_thread", description="Update an existing thread with new content")
def update_thread(ctx: Context, thread_id: str = Field(description="The thread ID"),
                  content: str = Field(description="The content to update in the thread")) -> TeamsMessage:
    client = ctx.request_context.lifespan_context["client"]
    return client.update_thread(thread_id, content)


@mcp.tool(name="mention_user", description="Mention user in an existing thread")
def mention_user(ctx: Context, thread_id: str = Field(description="The thread ID"), user_id: str = Field("The user ID"),
                 content: str = Field("Content to be added to the thread")) -> TeamsMessage:
    client = ctx.request_context.lifespan_context["client"]
    return client.mention_user(thread_id, user_id, content)


@mcp.tool(name="read_thread", description="Read replies in a thread")
def read_thread(ctx: Context, thread_id: str = Field(description="The thread ID")) -> List[TeamsMessage]:
    client = ctx.request_context.lifespan_context["client"]
    return client.read_thread(thread_id)


# TODO: get member id from a given name

# TODO: read threads in channel

# TODO: reply to message

@mcp.tool(name="list_members", description="List all members in the team")
def list_members(ctx: Context) -> List[TeamsMember]:
    client = ctx.request_context.lifespan_context["client"]
    return client.list_members()


@mcp.tool(name="add_reaction", description="Add reaction to a message")
def add_reaction(ctx: Context, message_id: str = Field("The message ID"),
                 reaction: str = Field("The reaction to be added")) -> TeamsMessage:
    client = ctx.request_context.lifespan_context["client"]
    return client.add_reaction(message_id, reaction)


def main() -> None:
    LOGGER.info(f"Starting MCP Teams Server {__version__}")
    mcp.run()


if __name__ == "__main__":
    main()
