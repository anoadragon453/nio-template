import logging

logger = logging.getLogger(__name__)

class SyncToken(object):
    """A SyncToken is an instance of a sync token, which is a token retrieved from a matrix
    homeserver. It is given to the /sync endpoint in order to specify at which point in the
    event timeline you would like to receive messages after
    """

    def __init__(self, store):
        """
        Args:
            store (Storage): An object to access the storage layer
        """
        self.store = store
        self.token = None

        # Attempt to load a token from the provided storage layer
        self._load()

    def _load(self):
        """Load the latest sync token from the database"""
        self.store.cursor.execute("SELECT token FROM sync_token")
        rows = self.store.cursor.fetchone()

        if rows:
            self.token = rows[0]

    def update(self, token):
        """Update the sync token in the database and the object

        Args:
            token (str): A sync token from a sync response sent by a matrix homeserver
        """
        self.token = token
        self.store.cursor.execute("INSERT OR REPLACE INTO sync_token "
                                  "(dedupe_id, token) VALUES (1, ?)", (token,))
        self.store.conn.commit()
