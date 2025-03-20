from typing import List, Dict, Any
import logging

from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsInfo
from botbuilder.integration.aiohttp import CloudAdapter
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    ConversationReference, ChannelAccount, ConversationAccount, Mention, MessageReaction, MessageReactionTypes,
)
from botbuilder.schema.teams import TeamsChannelAccount
from msgraph import GraphServiceClient
from msgraph.generated.teams.item.channels.item.messages.item.chat_message_item_request_builder import \
    ChatMessageItemRequestBuilder
from msrest.exceptions import HttpOperationError

LOGGER = logging.getLogger(__name__)


class TeamsClient:
    def __init__(self, adapter: CloudAdapter, graph_client: GraphServiceClient, teams_app_id: str, team_id: str,
                 teams_channel_id: str):
        self.adapter = adapter
        self.graph_client = graph_client
        self.teams_app_id = teams_app_id
        self.team_id = team_id
        self.teams_channel_id = teams_channel_id
        self.service_url = None
        self.adapter.on_turn_error = self.on_turn_error

    def get_team_id(self):
        return self.team_id

    @staticmethod
    async def on_turn_error(context: TurnContext, error: Exception):
        LOGGER.error(f"Error {error}")
        await context.send_activity("An error occurred in the bot, please try again later")

    def _create_conversation_reference(self) -> ConversationReference:
        service_url = "https://smba.trafficmanager.net/emea/"
        if self.service_url is not None:
            service_url = self.service_url
        return ConversationReference(
            bot=TeamsChannelAccount(id=self.teams_app_id, name="MCP Bot"),
            channel_id=self.teams_channel_id,
            service_url=service_url,
            conversation=ConversationAccount(id=self.teams_channel_id, is_group=True, conversation_type="channel",
                                             name="Teams channel")
        )

    async def _initialize(self) -> str:
        if not self.service_url:
            def context_callback(context: TurnContext):
                self.service_url = context.service_url

            await self.adapter.continue_conversation(bot_app_id=self.teams_app_id,
                                                     reference=self._create_conversation_reference(),
                                                     callback=context_callback)
        return self.service_url

    async def start_thread(
            self, title: str, content: str
    ) -> Dict[str, Any]:
        """Start a new thread in a channel.

        Args:
            title: Thread title
            content: Initial thread content

        Returns:
            Created thread details including ID
        """
        try:
            await self._initialize()

            result = {
                "title": title,
                "content": content
            }

            async def start_thread_callback(context: TurnContext):
                response = await context.send_activity(activity_or_text=Activity(
                    type=ActivityTypes.message,
                    topic_name=title,
                    text=content
                ))
                if response is not None:
                    result["thread_id"] = response.id

            await self.adapter.continue_conversation(bot_app_id=self.teams_app_id,
                                                     reference=self._create_conversation_reference(),
                                                     callback=start_thread_callback)

            return result
        except HttpOperationError as e:
            LOGGER.error(f"Error creating thread: {str(e)}")
            raise

    async def update_thread(
            self, thread_id: str, content: str
    ) -> Dict[str, str]:
        """Add a message to an existing thread.

        Args:
            thread_id: Thread ID to update
            content: Message content to add

        Returns:
            Updated thread details
        """
        try:
            await self._initialize()

            result = {
                "thread_id": thread_id,
                "content": content
            }

            async def update_thread_callback(context: TurnContext):
                response = await context.send_activity(activity_or_text=Activity(
                    type=ActivityTypes.message,
                    text=content,
                    conversation=ConversationAccount(id=thread_id)
                ))
                if response is not None:
                    result["message_id"] = response.id

            await self.adapter.continue_conversation(bot_app_id=self.teams_app_id,
                                                     reference=self._create_conversation_reference(),
                                                     callback=update_thread_callback)

            return result
        except HttpOperationError as e:
            LOGGER.error(f"Error updating thread: {str(e)}")
            raise

    # TODO: add reply to

    async def mention_user(
            self,
            thread_id: str,
            user_id: str,
            content: str
    ) -> Dict[str, str]:
        """Mention a user in a thread message.

        Args:
            thread_id: Thread ID to add mention
            user_id: ID of user to mention
            content: Message content

        Returns:
            Message details including IDs
        """
        try:
            await self._initialize()

            result = {
                "thread_id": thread_id,
                "user_id": user_id,
                "content": content
            }

            async def mention_user_callback(context: TurnContext):
                member = await TeamsInfo.get_team_member(context, self.team_id, user_id)
                if member is not None:
                    result["user_name"] = member.name

                mention = Mention(text=f"<at>{result.get('user_name')}</at>", type="mention",
                                  mentioned=ChannelAccount(id=user_id, name=result["user_name"]))

                response = await context.send_activity(activity_or_text=Activity(
                    type=ActivityTypes.message,
                    text=f'<at>{result["user_name"]}</at> {content}',
                    conversation=ConversationAccount(id=thread_id),
                    entities=[mention]
                ))
                if response is not None:
                    result["message_id"] = response.id

            await self.adapter.continue_conversation(bot_app_id=self.teams_app_id,
                                                     reference=self._create_conversation_reference(),
                                                     callback=mention_user_callback)

            return result
        except HttpOperationError as e:
            LOGGER.error(f"Error mentioning user: {str(e)}")
            raise

    async def read_thread(
            self, channel_id: str, thread_id: str
    ) -> List[Dict[str, Any]]:
        """Read all replies in a thread.

        Args:
            channel_id: Channel ID containing thread
            thread_id: Thread ID to read

        Returns:
            List of thread messages
        """
        try:
            request = ChatMessageItemRequestBuilder.ChatMessageItemRequestBuilderGetQueryParameters(expand=['replies'])
            message = await self.graph_client.teams.by_team_id(self.team_id).channels.by_channel_id(
                self.teams_channel_id).messages.by_chat_message_id(thread_id).get(request_configuration=request)

            result = []

            if message is not None:
                for reply in message.replies:
                    result.append({"message_id": reply.id, "content": reply.body.content})

            return result
        except HttpOperationError as e:
            LOGGER.error(f"Error reading thread: {str(e)}")
            raise

    async def list_members(self) -> List[Dict[str, Any]]:
        """List all members in the configured team.

        Returns:
            List of team member details
        """
        try:
            await self._initialize()
            result = []

            async def list_members_callback(context: TurnContext):
                members = await TeamsInfo.get_team_members(context, self.team_id)
                for member in members:
                    result.append(member)

            await self.adapter.continue_conversation(bot_app_id=self.teams_app_id,
                                                     reference=self._create_conversation_reference(),
                                                     callback=list_members_callback)
            return result
        except HttpOperationError as e:
            LOGGER.error(f"Error listing members: {str(e)}")
            raise

    async def add_reaction(
            self, channel_id: str, message_id: str, reaction: str
    ) -> Dict[str, str]:
        """Add a reaction to a message.

        Args:
            channel_id: Channel ID containing message
            message_id: Message ID to react to
            reaction: Reaction emoji name

        Returns:
            Reaction details
        """
        try:
            await self._initialize()

            result = {
                "message_id": message_id
            }

            async def add_reaction_callback(context: TurnContext):
                response = await context.send_activity(activity_or_text=Activity(
                    type=ActivityTypes.message,
                    reactions_added=[MessageReaction(type=MessageReactionTypes.like)],
                    reply_to_id=message_id
                ))

            await self.adapter.continue_conversation(bot_app_id=self.teams_app_id,
                                                     reference=self._create_conversation_reference(),
                                                     callback=add_reaction_callback)

            return result
        except HttpOperationError as e:
            LOGGER.error(f"Error adding reaction: {str(e)}")
            raise
