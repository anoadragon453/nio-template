import logging
import re
import os
import yaml
import sys
from typing import List, Any
from errors import ConfigError

logger = logging.getLogger()


class Config(object):
    def __init__(self, filepath):
        """
        Args:
            filepath (str): Path to config file
        """
        if not os.path.isfile(filepath):
            raise ConfigError(f"Config file '{filepath}' does not exist")

        # Load in the config file at the given filepath
        with open(filepath) as file_stream:
            self.config = yaml.safe_load(file_stream.read())

        # Logging setup
        formatter = logging.Formatter('%(asctime)s | %(name)s [%(levelname)s] %(message)s')

        log_level = self._get_cfg(["logging", "level"], default="INFO")
        logger.setLevel(log_level)

        file_logging_enabled = self._get_cfg(["logging", "file_logging", "enabled"], default=False)
        file_logging_filepath = self._get_cfg(["logging", "file_logging", "filepath"], default="bot.log")
        if file_logging_enabled:
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        console_logging_enabled = self._get_cfg(["logging", "console_logging", "enabled"], default=True)
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Database setup
        self.database_filepath = self._get_cfg(["database", "filepath"], required=True)

        # Matrix bot account setup
        self.user_id = self._get_cfg(["matrix", "user_id"], required=True)
        if not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        self.access_token = self._get_cfg(["matrix", "access_token"], required=True)

        self.device_id = self._get_cfg(["matrix", "device_id"])
        if not self.device_id:
            logger.warning(
                "Config option matrix.device_id is not provided, which means "
                "that end-to-end encryption won't work correctly"
            )

        self.homeserver_url = self._get_cfg(["matrix", "homeserver_url"], required=True)

        self.command_prefix = self._get_cfg(["command_prefix"], default="!c") + " "

    def _get_cfg(
            self,
            path: List[str],
            default: Any = None,
            required: bool = True,
    ) -> Any:
        """Get a config option from a path and option name, specifying whether it is
        required.

        Raises:
            ConfigError: If required is specified and the object is not found
                (and there is no default value provided), this error will be raised
        """
        path_str = '.'.join(path)

        # Sift through the the config until we reach our option
        config = self.config
        for name in path:
            print("Name is", name)
            config = config.get(name)
            print("Config is", config)

            # If at any point we don't get our expected option...
            if config is None:
                # Raise an error if it was required
                if required or not default:
                    raise ConfigError(f"Config option {path_str} is required")

                # or return the default value
                return default

        # We found the option. Return it
        return config
