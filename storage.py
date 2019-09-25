import sqlite3
import os.path

latest_db_version = 0


class Storage(object):
    def __init__(self, db_path):
        """Setup the database

        Runs an initial setup or migrations depending on whether a database file has already
        been created

        Args:
            db_path (str): The name of the database file
        """
        self.db_path = db_path

        # Check if a database has already been connected
        if os.path.isfile(self.db_path):
            self._run_migrations()
        else:
            self._initial_setup()

    def _initial_setup(self):
        """Initial setup of the database"""
        print("Performing initial setup")

        # Initialize a connection to the database
        conn = sqlite3.connect(self.db_path)
        self.cursor = conn.cursor()

        # Sync token table
        self.cursor.execute("CREATE TABLE sync_token ("
                            "token TEXT PRIMARY KEY"
                            ")")

    def _run_migrations(self):
        """Execute database migrations"""
        # Initialize a connection to the database
        conn = sqlite3.connect(self.db_path)
        self.cursor = conn.cursor()

        print("Running migration")
        pass

    def get_sync_token(self):
        """Retrieve the next_batch token from the last sync response.

        Used to sync without retrieving messages we've processed in the past

        Returns:
            A str containing the last sync token or None if one does not exist
        """
        self.cursor.execute("SELECT token FROM sync_token")
        rows = self.cursor.fetchone()

        if not rows:
            return None

        return rows[0]

    def save_sync_token(self, token):
        """Save a token from a sync response.

        Can be retrieved later to sync from where we left off

        Args:
            token (str): A next_batch token as part of a sync response
        """
        self.cursor.execute("INSERT OR REPLACE INTO sync_token"
                            " (token) VALUES (?)", (token,))
