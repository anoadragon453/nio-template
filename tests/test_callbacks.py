import unittest
from unittest.mock import Mock

import nio

from my_project_name.callbacks import Callbacks
from my_project_name.storage import Storage

from tests.utils import make_awaitable, run_coroutine


class CallbacksTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # Create a Callbacks object and give it some Mock'd objects to use
        self.fake_client = Mock(spec=nio.AsyncClient)
        self.fake_client.user = "@fake_user:example.com"

        self.fake_storage = Mock(spec=Storage)

        # We don't spec config, as it doesn't currently have well defined attributes
        self.fake_config = Mock()

        self.callbacks = Callbacks(
            self.fake_client, self.fake_storage, self.fake_config
        )

    def test_invite(self):
        """Tests the callback for InviteMemberEvents"""
        # Tests that the bot attempts to join a room after being invited to it

        # Create a fake room and invite event to call the 'invite' callback with
        fake_room = Mock(spec=nio.MatrixRoom)
        fake_room_id = "!abcdefg:example.com"
        fake_room.room_id = fake_room_id

        fake_invite_event = Mock(spec=nio.InviteMemberEvent)
        fake_invite_event.sender = "@some_other_fake_user:example.com"

        # Pretend that attempting to join a room is always successful
        self.fake_client.join.return_value = make_awaitable(None)

        # Pretend that we received an invite event
        run_coroutine(self.callbacks.invite(fake_room, fake_invite_event))

        # Check that we attempted to join the room
        self.fake_client.join.assert_called_once_with(fake_room_id)


if __name__ == "__main__":
    unittest.main()
