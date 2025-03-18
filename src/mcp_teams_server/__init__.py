from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib import metadata
from typing import AsyncIterator, List, Dict, Any, Optional

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botframework.connector.auth import ManagedIdentityAppCredentials, SimpleCredentialProvider, SimpleChannelProvider
from mcp.server.fastmcp import FastMCP, Context

from .teams import TeamsClient
import os
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

logger = logging.getLogger(__name__)

#
#   Bot resource link: https://portal.azure.com/#@inditex.cloud/resource/subscriptions/4b038ed6-da8c-4865-95a3-3ea3563b9d54/resourceGroups/cloudcotwo-rsg-esc1-pro-mcpteamsbot/providers/Microsoft.BotService/botServices/mcpteamsbot/overview
#

#
#   App manifest generator link: https://dev.teams.microsoft.com/apps/f1fb85f3-e33e-41ca-8afe-9cbcece21fcd
#

APP_ID = os.getenv("TEAMS_APP_ID")
APP_TENANT_ID = os.getenv("TEAMS_APP_TENANT_ID")
TEAMS_ID = os.getenv("TEAMS_CHANNEL_ID")
TEAMS_TENANT_ID = os.getenv("TEAMS_APP_TENANT_ID")


@dataclass
class AppContext:
    client: TeamsClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    settings = BotFrameworkAdapterSettings(
        app_id=APP_ID,
        app_credentials=ManagedIdentityAppCredentials(app_id=APP_ID)
    )
    adapter = BotFrameworkAdapter(settings)
    client = TeamsClient(adapter, TEAMS_ID, TEAMS_TENANT_ID)
    yield AppContext(client=client)


mcp = FastMCP("mcp-teams-server", lifespan=app_lifespan)


@mcp.tool(name="teams_greeting", description="Says a hello message from MCP Teams Server")
def teams_greeting(ctx: Context) -> str:
    """Says a hello message from MCP Teams Server"""
    client = ctx.request_context.lifespan_context["client"]
    return f'Hello from mcp-teams-server: {__version__} in team {client.get_team_id()}!'


@mcp.tool(name="list_channels", description="List all channels in the configured team")
def list_channels(ctx: Context) -> List[Dict[str, str]]:
    """List channels from MCP teams server"""
    client = ctx.request_context.lifespan_context["client"]
    return client.list_channels()


@mcp.tool(name="start_thread", description="Start a new thread in a channel")
def start_thread(ctx: Context, channel_id: str, title: str, content: str) -> Dict[str, str]:
    client = ctx.request_context.lifespan_context["client"]
    return client.start_thread(channel_id, title, content)


@mcp.tool(name="update_thread", description="Add a message to an existing thread")
def update_thread(ctx: Context, channel_id: str, thread_id: str, content: str) -> Dict[str, str]:
    client = ctx.request_context.lifespan_context["client"]
    return client.update_thread(channel_id, thread_id, content)


@mcp.tool(name="mention_user", description="Mention user in a thread")
def mention_user(ctx: Context, channel_id: str, thread_id: str, user_id: str, content: str) -> Dict[str, str]:
    client = ctx.request_context.lifespan_context["client"]
    return client.mention_user(channel_id, thread_id, user_id, content)


@mcp.tool(name="read_thread", description="Read replies in a thread")
def read_thread(ctx: Context, channel_id: str, thread_id: str) -> List[Dict[str, str]]:
    client = ctx.request_context.lifespan_context["client"]
    return client.read_thread(channel_id, thread_id)


@mcp.tool(name="list_members", description="List all members in the team")
def list_members(ctx: Context) -> List[Dict[str, str]]:
    client = ctx.request_context.lifespan_context["client"]
    return client.list_members()


@mcp.tool(name="add_reaction", description="Add reaction to a message")
def add_reaction(ctx: Context, channel_id: str, message_id: str, reaction: str) -> Dict[str, str]:
    client = ctx.request_context.lifespan_context["client"]
    return client.add_reaction(channel_id, message_id, reaction)


def main() -> None:
    logger.info(f"Starting MCP Teams Server {__version__}")
    mcp.run()
