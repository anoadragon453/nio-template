#!/usr/bin/env python3

import logging
import asyncio
from nio import (
    AsyncClient,
    AsyncClientConfig,
    RoomMessageText,
    InviteEvent,
    SyncError,
)
from callbacks import Callbacks
from config import Config
from storage import Storage
from sync_token import SyncToken

logger = logging.getLogger(__name__)


async def main():
    # Read config file
    config = Config("config.yaml")

    # Configure the database
    store = Storage(config.database_filepath)

    # Configuration options for the AsyncClient
    client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
    )

    # Initialize the matrix client
    client = AsyncClient(
        config.homeserver_url,
        config.user_id,
        device_id=config.device_id,
        config=client_config,
    )

    # Assign an access token to the bot instead of logging in and creating a new device
    client.access_token = config.access_token

    # Set up event callbacks
    callbacks = Callbacks(client, store, config.command_prefix)
    client.add_event_callback(callbacks.message, (RoomMessageText,))
    client.add_event_callback(callbacks.invite, (InviteEvent,))

    # Create a new sync token, attempting to load one from the database if it has one already
    sync_token = SyncToken(store)

    # Sync loop
    while True:
        # Sync with the server
        sync_response = await client.sync(timeout=30000, full_state=True,
                                          since=sync_token.token)

        # Check if the sync had an error
        if type(sync_response) == SyncError:
            logger.warning("Error in client sync: %s", sync_response.message)
            continue

        # Save the latest sync token to the database
        token = sync_response.next_batch
        if token:
            sync_token.update(token)

asyncio.get_event_loop().run_until_complete(main())
