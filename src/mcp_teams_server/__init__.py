import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib import metadata
from typing import AsyncIterator, List
from pydantic import Field

from azure.identity.aio import ClientSecretCredential
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from mcp.server.fastmcp import FastMCP, Context
from msgraph import GraphServiceClient

from .config import BotConfiguration
from .teams import TeamsClient, TeamsMessage, TeamsThread, TeamsMember, PagedTeamsMessages
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

REQUIRED_ENV_VARS = ["TEAMS_APP_ID", "TEAMS_APP_PASSWORD", "TEAMS_APP_TYPE", "TEAMS_APP_TENANT_ID", "TEAM_ID",
                     "TEAMS_CHANNEL_ID"]


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
        bot_config.APP_ID,
        bot_config.APP_PASSWORD
    )
    scopes = ['https://graph.microsoft.com/.default']
    graph_client = GraphServiceClient(credentials=credentials, scopes=scopes)

    client = TeamsClient(adapter, graph_client, bot_config.APP_ID, bot_config.TEAM_ID, bot_config.TEAMS_CHANNEL_ID)
    yield AppContext(client=client)


mcp = FastMCP("mcp-teams-server", lifespan=app_lifespan)


def _get_teams_client(ctx: Context) -> TeamsClient:
    return ctx.request_context.lifespan_context.client


@mcp.tool(name="start_thread", description="Start a new thread with a given title and content")
async def start_thread(ctx: Context, title: str = Field(description="The thread title"),
                       content: str = Field(description="The thread content")) -> TeamsThread:
    await ctx.debug(f"start_thread with title={title} and content={content}")
    client = _get_teams_client(ctx)
    return await client.start_thread(title, content)


@mcp.tool(name="update_thread", description="Update an existing thread with new content")
async def update_thread(ctx: Context, thread_id: str = Field(description="The thread ID as a string in the format '1743086901347'"),
                        content: str = Field(description="The content to update in the thread")) -> TeamsMessage:
    await ctx.debug(f"update_thread with thread_id={thread_id} and content={content}")
    client = _get_teams_client(ctx)
    return await client.update_thread(thread_id, content)


@mcp.tool(name="mention_member", description="Mention a member in an existing thread")
async def mention_member(ctx: Context, thread_id: str = Field(description="The thread ID as a string in the format '1743086901347'"),
                       member_name: str = Field("The member name"),
                       content: str = Field("Content to be added to the thread")) -> TeamsMessage:
    await ctx.debug(f"mention_member in thread_id={thread_id}, member_name={member_name} and content={content}")
    client = _get_teams_client(ctx)
    return await client.mention_member(thread_id, member_name, content)


@mcp.tool(name="read_thread", description="Read replies in a thread")
async def read_thread(ctx: Context, thread_id: str = Field(description="The thread ID as a string in the format '1743086901347'")) -> PagedTeamsMessages:
    await ctx.debug(f"read_thread with thread_id={thread_id}")
    client = _get_teams_client(ctx)
    return await client.read_thread_replies(thread_id, 0, 100)


@mcp.tool(name="list_threads", description="List threads in channel with pagination")
async def list_threads(ctx: Context,
                       offset: int = Field(description="Offset of the first thread to retrieve, used for pagination.",
                                           default=0),
                       limit: int = Field(
                           description="Maximum number of items to retrieve or page size",
                           default=50)) -> PagedTeamsMessages:
    await ctx.debug(f"list_threads with offset={offset} and limit={limit}")
    client = _get_teams_client(ctx)
    return await client.read_threads(offset, limit)


@mcp.tool(name="get_member_by_name", description="Get a member by its name")
async def get_member_by_name(ctx: Context, name: str = Field(description="Member name")):
    await ctx.debug(f"get_member_by_name with name={name}")
    client = _get_teams_client(ctx)
    return await client.get_member_by_name(name)


@mcp.tool(name="list_members", description="List all members in the team")
async def list_members(ctx: Context) -> List[TeamsMember]:
    await ctx.debug(f"list_members")
    client = _get_teams_client(ctx)
    return await client.list_members()


def _check_required_environment():
    exit_code = None
    for var in REQUIRED_ENV_VARS:
        value = os.environ.get(var)
        if value is None:
            LOGGER.info(f"Required ENV {var} not present")
            exit_code = 1
    if exit_code is not None:
        sys.exit(exit_code)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="MCP Teams Server to allow Microsoft Teams interaction"
    )
    parser.add_argument("-t", "--transport", nargs=1, type=str, help="MCP Server Transport: stdio or sse",
                        default="stdio",
                        choices=["stdio", "sse"])

    args = parser.parse_args()

    LOGGER.info(f"Starting MCP Teams Server \"{__version__}\" with transport \"{args.transport}\"")
    _check_required_environment()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
