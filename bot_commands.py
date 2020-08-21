#!/usr/bin/env python3

r"""bot_commands.py.

0123456789012345678901234567890123456789012345678901234567890123456789012345678
0000000000111111111122222222223333333333444444444455555555556666666666777777777

# bot_commands.py

See the implemented sample bot commands of `echo`, `date`, `dir`, `help`,
and `whoami`? Have a close look at them and style your commands after these
example commands.

Don't change tabbing, spacing, or formating as the
file is automatically linted and beautified.

"""

import getpass
import logging
import os
import re  # regular expression matching
import subprocess
from sys import platform
import traceback
from chat_functions import send_text_to_room

logger = logging.getLogger(__name__)

SERVER_ERROR_MSG = "Bot encountered an error. Here is the stack trace: \n"


class Command(object):
    """Use this class for your bot commands."""

    def __init__(self, client, store, config, command, room, event):
        """Set up bot commands.

        Arguments:
        ---------
            client (nio.AsyncClient): The client to communicate with Matrix
            store (Storage): Bot storage
            config (Config): Bot configuration parameters
            command (str): The command and arguments
            room (nio.rooms.MatrixRoom): The room the command was sent in
            event (nio.events.room_events.RoomMessageText): The event
                describing the command

        """
        self.client = client
        self.store = store
        self.config = config
        self.command = command
        self.room = room
        self.event = event
        self.args = self.command.split()[1:]
        self.commandlower = self.command.lower()

    async def process(self):  # noqa
        """Process the command."""

        logger.debug(
            f"bot_commands :: Command.process: {self.command} {self.room}")
        # echo
        if re.match("^echo$|^echo .*", self.commandlower):
            await self._echo()
        # help
        elif re.match("^help$|^ayuda$|^man$|^manual$|^hilfe$|"
                      "^je suis perdu$|^perdu$|^socorro$|^h$|"
                      "^rescate$|^rescate .*|^help .*|^help.sh$",
                      self.commandlower):
            await self._show_help()
        # list directory
        elif re.match("^list$|^ls$|^dir$|^directory$", self.commandlower):
            # Just an example how to call OS commands,
            # or how to call shell scripts, .bat files, etc.
            # Prepare the command with arguments and pass it into
            # await self._os_cmd().
            # You don't need to distinguish platforms. You need to prepare
            # the command only for 1 platform, your platform, for the platform
            # where you will run the bot.
            if (platform == "linux" or platform == "linux2" or
                    platform == "cygwin"):
                # linux, linux-like
                list_cmd = "ls -al"
            elif platform == "darwin":
                # OS X, Mac
                list_cmd = "ls"
            elif platform == "win32" or platform == "windows":
                # Windows...
                list_cmd = "dir"
            else:
                # Java, OpenVMS, etc.
                logger.debug("Operating system or platform not supported "
                             "for the \"list\" command. Sorry.")
                return
            await self._os_cmd(cmd=list_cmd,
                               markdown_convert=False, formatted=True,
                               code=True)
        # show date (and time on linux)
        elif re.match("^date$|^datum$|^data$|^fecha$|"
                      "^time$|^hora$|^heure$|^uhrzeit$", self.commandlower):
            # Just an example how to call OS commands,
            # or how to call shell scripts, .bat files, etc.
            # Prepare the command with arguments and pass it into
            # await self._os_cmd().
            # You don't need to distinguish platforms. You need to prepare
            # the command only for 1 platform, your platform, for the platform
            # where you will run the bot.
            if (platform == "linux" or platform == "linux2" or
                    platform == "cygwin"):
                # linux, linux-like
                date_cmd = "date --utc"
            elif platform == "darwin":
                # OS X, Mac
                date_cmd = "date"
            elif platform == "win32" or platform == "windows":
                # Windows...
                date_cmd = "DATE /T"
            else:
                # Java, OpenVMS, etc.
                logger.debug("Operating system or platform not supported "
                             "for the \"list\" command. Sorry.")
                return
            await self._os_cmd(cmd=date_cmd,
                               markdown_convert=False, formatted=True,
                               code=True)
        # whoami
        elif re.match("^w$|^who$|^whoami$", self.commandlower):
            await self._whoami()
        # # add your own commands here
        # # short description of your command
        # elif re.match("^your-regular-expression", self.commandlower):
        #    await self._your_command_function()
        # # and repeat this for every command in your bot

        else:
            await self._unknown_command()

    async def _echo(self):
        """Echo back the command's arguments."""
        response = " ".join(self.args)
        if response.strip() == "":
            response = "echo!"
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _whoami(self):
        """whoami."""
        response = (f"- user name: `{getpass.getuser()}`\n"
                    f"- home: `{os.environ['HOME']}`\n"
                    f"- path: `{os.environ['PATH']}`")
        await send_text_to_room(self.client, self.room.room_id, response,
                                markdown_convert=True, formatted=True)

    async def _show_help(self):
        """Show the help text."""
        if not self.args:
            response = ("Hello, I am your bot! "
                        "Use `help all` or `help commands` to view "
                        "available commands.")
            await send_text_to_room(self.client, self.room.room_id, response)
            return

        topic = self.args[0]
        if topic == "rules":
            response = "These are the rules: Act responsibly."
        elif topic == "commands" or topic == "all":
            await self._os_cmd(cmd="help.sh",
                               markdown_convert=True, formatted=True,
                               code=False)
            return
        else:
            response = f"Unknown help topic `{topic}`!"
        await send_text_to_room(self.client, self.room.room_id, response)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            (f"Unknown command `{self.command}`. "
             "Try the `help` command for more information."))

    async def _os_cmd(self, cmd, markdown_convert=True,
                      formatted=True, code=False, split=None):
        """Pass generic command on to the operating system.

        cmd (str): string of the command including any arguments,
            make sure command is found
            by operating system in its PATH for executables
            e.g. "date" for OS date command.
            Valid example of cmd: "date --utc"
            Invalid example for cmd: "echo 'Date'; date --utc"
            Invalid example for cmd: "echo 'Date' && date --utc"
            Invalid example for cmd: "TZ='America/Los_Angeles' date --utc"
            If you have commands that consist of more than 1 command,
            put them into a shell or .bat script and call that script
            with any necessary arguments.
        markdown_convert (bool): value for how to format response
        formatted (bool): value for how to format response
        code (bool): value for how to format response
        """
        try:
            # need to convert string `cmd` to list like
            # ['date', '--utc']
            argv_list = cmd.split()
            logger.debug(f"OS command \"{argv_list[0]}\" with "
                         f"args: \"{argv_list[1:]}\"")
            run = subprocess.Popen(
                argv_list,  # list of argv
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            output, std_err = run.communicate()
            output = output.strip()
            std_err = std_err.strip()
            if run.returncode != 0:
                logger.debug(f"Bot command {cmd} exited with return "
                             f"code {run.returncode} and "
                             f"stderr as \"{std_err}\" and "
                             f"stdout as \"{output}\"")
                output = (f"*** Error: command {cmd} returned error "
                          f"code {run.returncode}. ***\n{std_err}\n{output}")
            response = output
        except Exception:
            response = SERVER_ERROR_MSG + traceback.format_exc()
            code = True  # format stack traces as code
        logger.debug(f"Sending this reply back: {response}")
        await send_text_to_room(self.client, self.room.room_id, response,
                                markdown_convert=markdown_convert,
                                formatted=formatted, code=code, split=split)


# EOF
