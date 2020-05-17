import os
import logging
from time import sleep
from nio import (
    AsyncClient,
    AsyncClientConfig,
    RoomMessageText,
    InviteMemberEvent,
    LoginError,
    LocalProtocolError,
)
from aiohttp import (
    ServerDisconnectedError,
    ClientConnectionError
)
from matrixbot.callbacks import Callbacks
from matrixbot.config import Config
from matrixbot.storage import Storage

logger = logging.getLogger(__name__)


class Bot():

    def __init__(self, config_filepath):
        # Read config file
        self.config = Config(config_filepath)

        # Configure the database
        store = Storage(self.config.database_filepath)

        # Configuration options for the AsyncClient
        client_config = AsyncClientConfig(
            max_limit_exceeded=0,
            max_timeouts=0,
            store_sync_tokens=True,
            encryption_enabled=self.config.enable_encryption,
        )

        # Initialize the matrix client
        self.client = AsyncClient(
            self.config.homeserver_url,
            self.config.user_id,
            device_id=self.config.device_id,
            store_path=self.config.store_filepath,
            config=client_config,
        )

        # Set up event callbacks
        self.callbacks = Callbacks(self.client, store, self.config)
        self.client.add_event_callback(self.callbacks.message, (RoomMessageText,))
        self.client.add_event_callback(self.callbacks.invite, (InviteMemberEvent,))


    async def login(self):
        # Keep trying to reconnect on failure (with some time in-between)
        while True:
            try:
                # Try to login with the configured username/password
                try:
                    login_response = await self.client.login(
                        password=self.config.user_password,
                        device_name=self.config.device_name,
                    )

                    # Check if login failed
                    if type(login_response) == LoginError:
                        logger.error(f"Failed to login: %s", login_response.message)
                        return False
                except LocalProtocolError as e:
                    # There's an edge case here where the user enables encryption but hasn't installed
                    # the correct C dependencies. In that case, a LocalProtocolError is raised on login.
                    # Warn the user if these conditions are met.
                    if config.enable_encryption:
                        logger.fatal(
                            "Failed to login and encryption is enabled. Have you installed the correct dependencies? "
                            "https://github.com/poljar/matrix-nio#installation"
                        )
                        return False
                    else:
                        # We don't know why this was raised. Throw it at the user
                        logger.fatal("Error logging in: %s", e)
                        return False

                # Login succeeded!

                # Sync encryption keys with the server
                # Required for participating in encrypted rooms
                if self.client.should_upload_keys:
                    await self.client.keys_upload()

                logger.info(f"Logged in as {self.config.user_id}")
                await self.client.sync_forever(timeout=30000, full_state=True)

            except (ClientConnectionError, ServerDisconnectedError):
                logger.warning("Unable to connect to homeserver, retrying in 15s...")

                # Sleep so we don't bombard the server with login requests
                sleep(15)
            finally:
                # Make sure to close the client connection on disconnect
                await self.client.close()
