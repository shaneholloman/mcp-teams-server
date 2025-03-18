from typing import List, Dict, Any
import logging
from botbuilder.core import BotFrameworkAdapter
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    ConversationParameters,
)
from botbuilder.schema.teams import TeamsChannelData
from botframework.connector.aio import ConnectorClient
from msrest.exceptions import HttpOperationError

logger = logging.getLogger(__name__)


class TeamsClient:
    def __init__(self, adapter: BotFrameworkAdapter, team_id: str, teams_tenant_id: str):
        self.adapter = adapter
        self.team_id = team_id
        self.teams_tenant_id = teams_tenant_id
        self.connector_client = None

    def get_team_id(self):
        return self.team_id

    async def _get_connector(self) -> ConnectorClient:
        if not self.connector_client:
            self.connector_client = await self.adapter.create_connector_client("https:://smba.trafficmanager.net/emea/")
        return self.connector_client

    async def list_channels(self) -> List[Dict[str, Any]]:
        """List all channels in the configured team.

        Returns:
            List of channel objects containing id and name
        """
        try:
            connector = await self._get_connector()
            channels = await connector.teams.get_teams_channels(self.team_id)
            return [
                {"id": channel.id, "name": channel.name}
                for channel in channels.value
            ]
        except HttpOperationError as e:
            logger.error(f"Error listing channels: {str(e)}")
            raise

    async def start_thread(
            self, channel_id: str, title: str, content: str
    ) -> Dict[str, Any]:
        """Start a new thread in a channel.

        Args:
            channel_id: Channel ID to create thread in
            title: Thread title
            content: Initial thread content

        Returns:
            Created thread details including ID
        """
        try:
            connector = await self._get_connector()

            # Create conversation parameters
            params = ConversationParameters(
                is_group=True,
                channel_data=TeamsChannelData(channel={"id": channel_id}),
                activity=Activity(
                    type=ActivityTypes.message,
                    text=content,
                    topic=title,
                ),
                tenant_id=self.teams_tenant_id,
            )

            conv_ref = await connector.conversations.create_conversation(params)
            return {
                "thread_id": conv_ref.id,
                "title": title,
                "content": content
            }
        except HttpOperationError as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise

    async def update_thread(
            self, channel_id: str, thread_id: str, content: str
    ) -> Dict[str, str]:
        """Add a message to an existing thread.

        Args:
            channel_id: Channel ID containing thread
            thread_id: Thread ID to update
            content: Message content to add

        Returns:
            Updated thread details
        """
        try:
            connector = await self._get_connector()

            activity = Activity(
                type=ActivityTypes.message,
                text=content,
                conversation={"id": thread_id},
                channel_data=TeamsChannelData(channel={"id": channel_id}),
            )

            result = await connector.conversations.send_to_conversation(
                thread_id, activity
            )

            return {
                "thread_id": thread_id,
                "message_id": result.id,
                "content": content
            }
        except HttpOperationError as e:
            logger.error(f"Error updating thread: {str(e)}")
            raise

    async def mention_user(
            self,
            channel_id: str,
            thread_id: str,
            user_id: str,
            content: str
    ) -> Dict[str, str]:
        """Mention a user in a thread message.

        Args:
            channel_id: Channel ID containing thread
            thread_id: Thread ID to add mention
            user_id: ID of user to mention
            content: Message content

        Returns:
            Message details including IDs
        """
        try:
            connector = await self._get_connector()

            # Get user details
            member = await connector.conversations.get_conversation_member(
                thread_id, user_id
            )

            mention_text = f"<at>{member.name}</at> {content}"
            mention_entity = {
                "type": "mention",
                "text": f"<at>{member.name}</at>",
                "mentioned": {
                    "id": user_id,
                    "name": member.name,
                },
            }

            activity = Activity(
                type=ActivityTypes.message,
                text=mention_text,
                entities=[mention_entity],
                conversation={"id": thread_id},
                channel_data=TeamsChannelData(channel={"id": channel_id}),
            )

            result = await connector.conversations.send_to_conversation(
                thread_id, activity
            )

            return {
                "thread_id": thread_id,
                "message_id": result.id,
                "mentioned_user": member.name,
                "content": content
            }
        except HttpOperationError as e:
            logger.error(f"Error mentioning user: {str(e)}")
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
            connector = await self._get_connector()

            activities = await connector.conversations.get_conversation_activities(
                thread_id
            )

            return [
                {
                    "id": msg.id,
                    "content": msg.text,
                    "created": msg.timestamp.isoformat(),
                    "from": msg.from_property.name
                    if msg.from_property else None
                }
                for msg in activities
                if msg.type == ActivityTypes.message
            ]
        except HttpOperationError as e:
            logger.error(f"Error reading thread: {str(e)}")
            raise

    async def list_members(self) -> List[Dict[str, Any]]:
        """List all members in the configured team.

        Returns:
            List of team member details
        """
        try:
            connector = await self._get_connector()
            members = await connector.conversations.get_conversation_members(
                self.team_id
            )
            return [
                {
                    "id": member.id,
                    "name": member.name,
                    "email": member.email
                }
                for member in members
            ]
        except HttpOperationError as e:
            logger.error(f"Error listing members: {str(e)}")
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
            connector = await self._get_connector()

            activity = Activity(
                type=ActivityTypes.message_reaction,
                reaction_type=reaction,
                conversation={"id": channel_id},
                reply_to_id=message_id,
            )

            await connector.conversations.send_to_conversation(
                channel_id, activity
            )

            return {
                "message_id": message_id,
                "channel_id": channel_id,
                "reaction": reaction
            }
        except HttpOperationError as e:
            logger.error(f"Error adding reaction: {str(e)}")
            raise
