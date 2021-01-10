# This file holds custom error types that you can define for your application.


class ConfigError(RuntimeError):
    """An error encountered during reading the config file.

    Args:
        msg: The message displayed to the user on error.
    """

    def __init__(self, msg: str):
        super(ConfigError, self).__init__("%s" % (msg,))
