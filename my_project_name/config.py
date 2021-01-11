import logging
import os
import re
import sys
from typing import Any, List, Optional

import yaml

from my_project_name.errors import ConfigError

logger = logging.getLogger()
logging.getLogger("peewee").setLevel(
    logging.INFO
)  # Prevent debug messages from peewee lib


class Config:
    """Creates a Config object from a YAML-encoded config file from a given filepath"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.isfile(filepath):
            raise ConfigError(f"Config file '{filepath}' does not exist")

        # Load in the config file at the given filepath
        with open(filepath) as file_stream:
            self.config_dict = yaml.safe_load(file_stream.read())

        # Parse and validate config options
        self._parse_config_values()

    def _parse_config_values(self):
        """Read and validate each config option"""
        # Logging setup
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s [%(levelname)s] %(message)s"
        )

        log_level = self._get_cfg(["logging", "level"], default="INFO")
        logger.setLevel(log_level)

        file_logging_enabled = self._get_cfg(
            ["logging", "file_logging", "enabled"], default=False
        )
        file_logging_filepath = self._get_cfg(
            ["logging", "file_logging", "filepath"], default="bot.log"
        )
        if file_logging_enabled:
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        console_logging_enabled = self._get_cfg(
            ["logging", "console_logging", "enabled"], default=True
        )
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Storage setup
        self.store_path = self._get_cfg(["storage", "store_path"], required=True)

        # Create the store folder if it doesn't exist
        if not os.path.isdir(self.store_path):
            if not os.path.exists(self.store_path):
                os.mkdir(self.store_path)
            else:
                raise ConfigError(
                    f"storage.store_path '{self.store_path}' is not a directory"
                )

        # Database setup
        database_path = self._get_cfg(["storage", "database"], required=True)

        # Support both SQLite and Postgres backends
        # Determine which one the user intends
        sqlite_scheme = "sqlite://"
        postgres_scheme = "postgres://"
        if database_path.startswith(sqlite_scheme):
            self.database = {
                "type": "sqlite",
                "connection_string": database_path[len(sqlite_scheme) :],
            }
        elif database_path.startswith(postgres_scheme):
            self.database = {"type": "postgres", "connection_string": database_path}
        else:
            raise ConfigError("Invalid connection string for storage.database")

        # Matrix bot account setup
        self.user_id = self._get_cfg(["matrix", "user_id"], required=True)
        if not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        self.user_password = self._get_cfg(["matrix", "user_password"], required=False)
        self.user_token = self._get_cfg(["matrix", "user_token"], required=False)
        if not self.user_token and not self.user_password:
            raise ConfigError("Must supply either user token or password")

        self.device_id = self._get_cfg(["matrix", "device_id"], required=True)
        self.device_name = self._get_cfg(
            ["matrix", "device_name"], default="nio-template"
        )
        self.homeserver_url = self._get_cfg(["matrix", "homeserver_url"], required=True)

        self.command_prefix = self._get_cfg(["command_prefix"], default="!c") + " "

    def _get_cfg(
        self,
        path: List[str],
        default: Optional[Any] = None,
        required: Optional[bool] = True,
    ) -> Any:
        """Get a config option from a path and option name, specifying whether it is
        required.

        Raises:
            ConfigError: If required is True and the object is not found (and there is
                no default value provided), a ConfigError will be raised.
        """
        # Sift through the the config until we reach our option
        config = self.config_dict
        for name in path:
            config = config.get(name)

            # If at any point we don't get our expected option...
            if config is None:
                # Raise an error if it was required
                if required and not default:
                    raise ConfigError(f"Config option {'.'.join(path)} is required")

                # or return the default value
                return default

        # We found the option. Return it.
        return config
