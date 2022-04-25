import logging
from typing import Any, Dict

# The latest migration version of the database.
#
# Database migrations are applied starting from the number specified in the database's
# `migration_version` table + 1 (or from 0 if this table does not yet exist) up until
# the version specified here.
#
# When a migration is performed, the `migration_version` table should be incremented.
latest_migration_version = 0

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, database_config: Dict[str, str]):
        """Setup the database.

        Runs an initial setup or migrations depending on whether a database file has already
        been created.

        Args:
            database_config: a dictionary containing the following keys:
                * type: A string, one of "sqlite" or "postgres".
                * connection_string: A string, featuring a connection string that
                    be fed to each respective db library's `connect` method.
        """
        self.conn = self._get_database_connection(
            database_config["type"], database_config["connection_string"]
        )
        self.cursor = self.conn.cursor()
        self.db_type = database_config["type"]

        # Try to check the current migration version
        migration_level = 0
        try:
            self._execute("SELECT version FROM migration_version")
            row = self.cursor.fetchone()
            migration_level = row[0]
        except Exception:
            self._initial_setup()
        finally:
            if migration_level < latest_migration_version:
                self._run_migrations(migration_level)

        logger.info(f"Database initialization of type '{self.db_type}' complete")

    def _get_database_connection(
        self, database_type: str, connection_string: str
    ) -> Any:
        """Creates and returns a connection to the database"""
        if database_type == "sqlite":
            import sqlite3

            # Initialize a connection to the database, with autocommit on
            return sqlite3.connect(connection_string, isolation_level=None)
        elif database_type == "postgres":
            import psycopg2

            conn = psycopg2.connect(connection_string)

            # Autocommit on
            conn.set_isolation_level(0)

            return conn

    def _initial_setup(self) -> None:
        """Initial setup of the database"""
        logger.info("Performing initial database setup...")

        # Set up the migration_version table
        self._execute(
            """
            CREATE TABLE migration_version (
                version INTEGER PRIMARY KEY
            )
        """
        )

        # Initially set the migration version to 0
        self._execute(
            """
            INSERT INTO migration_version (
                version
            ) VALUES (?)
        """,
            (0,),
        )

        # Set up the improperly sent message table
        self._execute(
            """
            CREATE TABLE fails (
                user_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                attempts INTEGER DEFAULT 0
            )
            """
        )

        # Create a unique index on room_id, user_id
        self._execute(
            """
            CREATE UNIQUE INDEX fail_id
            ON fails(user_id, room_id)
        """
        )

        # Set up any other necessary database tables here

        logger.info("Database setup complete")

    def _run_migrations(self, current_migration_version: int) -> None:
        """Execute database migrations. Migrates the database to the
        `latest_migration_version`.

        Args:
            current_migration_version: The migration version that the database is
                currently at.
        """
        logger.debug("Checking for necessary database migrations...")

        # if current_migration_version < 1:
        #    logger.info("Migrating the database from v0 to v1...")
        #
        #    # Add new table, delete old ones, etc.
        #
        #    # Update the stored migration version
        #    self._execute("UPDATE migration_version SET version = 1")
        #
        #    logger.info("Database migrated to v1")

    def _execute(self, *args) -> None:
        """A wrapper around cursor.execute that transforms placeholder ?'s to %s for postgres.

        This allows for the support of queries that are compatible with both postgres and sqlite.

        Args:
            args: Arguments passed to cursor.execute.
        """
        if self.db_type == "postgres":
            self.cursor.execute(args[0].replace("?", "%s"), *args[1:])
        else:
            self.cursor.execute(*args)

    def update_or_create_fail(self, user_id, room_id):
        """Create a new fail entry, or increment an existing one"""
        logger.debug(f"Creating new/incrementing attempts for {user_id} in room {room_id}")
        self._execute(
            """
            INSERT INTO fails (
                user_id,
                room_id,
                attempts
            ) VALUES(
                ?, ?, 1
            )
            ON CONFLICT (user_id, room_id) DO
            UPDATE SET attempts = attempts + 1
        """,
            (
                user_id,
                room_id,
            ),
        )
#WHERE room_id = ? AND user_id = ?
    def delete_fail(self, user_id: str, room_id: str):
        """Delete a fail entry via its user and room ids"""
        self._execute(
            """
            DELETE FROM fails WHERE room_id = ? AND user_id = ?
        """,
            (room_id, user_id),
        )
    def get_fail(self, user_id, room_id):
        """ Get the number of fails for a user in a group"""

        self._execute(
            """
            SELECT attempts from fails 
            WHERE room_id = ? AND user_id = ?
        """,
            (
                room_id,
                user_id,
            ),
        )

        row = self.cursor.fetchall()
        if len(row) != 0:
            logger.debug(f"Found failed attempts for {user_id} in room {room_id}: {row[0][0]}")
            return row[0][0]
        logger.debug(f"First failed attempt for {user_id} in room {room_id}")
        return 0