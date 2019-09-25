import logging
from nio import (
    SendRetryError
)
from markdown import markdown

logger = logging.getLogger(__name__)


async def send_text_to_room(client, room_id, message, markdown_convert=True):
    """Send text to a matrix room

    Args:
        client (nio.AsyncClient): The client to communicate to matrix with

        room_id (str): The ID of the room to send the message to

        message (str): The message content

        markdown_convert (bool): Whether to convert the message content to markdown.
            Defaults to true.
    """
    formatted = message
    if markdown_convert:
        formatted = markdown(message)

    try:
        await client.room_send(
            room_id,
            "m.room.message",
            {
                "msgtype": "m.text",
                "format": "org.matrix.custom.html",
                "body": message,
                "formatted_body": formatted,
            }
        )
    except SendRetryError:
        logger.exception(f"Unable to send message response to {room_id}")
