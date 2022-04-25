from nio import AsyncClient, MatrixRoom, RoomMessageText, RoomRedactResponse
import logging

from my_project_name.chat_functions import react_to_event, send_text_to_room, send_msg, set_user_power
from my_project_name.config import Config
from my_project_name.storage import Storage

logger = logging.getLogger(__name__)

class Command:
    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        command: str,
        room: MatrixRoom,
        event: RoomMessageText,
    ):
        """A command made by a user.

        Args:
            client: The client to communicate to matrix with.

            store: Bot storage.

            config: Bot configuration parameters.

            command: The command and arguments.

            room: The room the command was sent in.

            event: The event describing the command.
        """
        self.client = client
        self.store = store
        self.config = config
        self.command = command
        self.room = room
        self.event = event
        self.args = self.command.split()[1:]

    async def process(self):
        """Process the command"""
        if self.command.startswith("echo"):
            await self._echo()
        elif self.command.startswith("react"):
            await self._react()
        elif self.command.startswith("help"):
            await self._show_help()
        #else:
            #await self._unknown_command()

    async def _echo(self):
        """Echo back the command's arguments"""
        response = " ".join(self.args)
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _react(self):
        """Make the bot react to the command message"""
        # React with a start emoji
        reaction = "⭐"
        await react_to_event(
            self.client, self.room.room_id, self.event.event_id, reaction
        )

        # React with some generic text
        reaction = "Some text"
        await react_to_event(
            self.client, self.room.room_id, self.event.event_id, reaction
        )

    async def _show_help(self):
        """Show the help text"""
        if not self.args:
            text = (
                "Hello, I am a bot made with matrix-nio! Use `help commands` to view "
                "available commands."
            )
            await send_text_to_room(self.client, self.room.room_id, text)
            return

        topic = self.args[0]
        if topic == "rules":
            text = "These are the rules!"
        elif topic == "commands":
            text = "Available commands: ..."
        else:
            text = "Unknown help topic!"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )
    
    async def filter_channel(self):
        # First check the power level of the sender. 0 - default, 50 - moderator, 100 - admin, others - custom.
        logger.debug(
            f"{self.room.user_name(self.event.sender)} has power level: {self.room.power_levels.get_user_level(self.event.sender)}"
        )
        if self.room.power_levels.get_user_level(self.event.sender) < 50:
            if self.room.power_levels.can_user_redact(self.client.user_id):
                
               # if not msg_room or (type(msg_room) is RoomCreateError):
        #logger.error(f'Unable to create room when trying to message {mxid}')
       #return False

                # Redact the message
                tries = 0
                redact_response = None
                while(type(redact_response) is not RoomRedactResponse and tries <3):
                    redact_response = await self.client.room_redact(self.room.room_id, self.event.event_id, "You are not a moderator of this channel.")
                    tries+=1
                if type(redact_response) is not RoomRedactResponse:
                    logger.error(f"Unable to redact message: {redact_response}")

                # Get user attempts from database
                fails = self.store.get_fail(self.event.sender, self.room.room_id)

                # Ban or increment attempts
                if fails < 3:
                    self.store.update_or_create_fail(self.event.sender, self.room.room_id)
                    await send_msg(self.client, self.event.sender, "WARNING!" ,f"Your comment has been deleted {fails+1} times in {self.room.room_id} discussion due to being improperly sent. Please reply in threads.")
                else:
                    logger.info(f"{self.room.user_name(self.event.sender)} has been banned from room {self.room.room_id}")
                    # Delete the user attempt entry
                    self.store.delete_fail(self.event.sender, self.room.room_id)

                    # Mute user
                    await set_user_power(self.room.room_id, self.event.sender, self.client, -1)
                    # Inform user about the ban
                    await send_msg(self.client, self.event.sender, "WARNING!" ,f"You have made >3 improper comments in {self.room.room_id} discussion. Please seek help from the group admin")
            else:
                logger.error(f"Bot does not have sufficient power to redact others in group: {self.room.room_id}")
