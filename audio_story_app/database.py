import sqlite3
import os
from datetime import datetime


class Database:
    """Handle database operations for the Audio Story App."""

    def __init__(self, db_path='data/audio_story.db'):
        """Initialize the database connection and create tables if needed."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        # Create recordings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            filepath TEXT NOT NULL,
            duration REAL,
            date_created TEXT,
            cover_art TEXT
        )
        ''')

        # Create playlists table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            date_created TEXT
        )
        ''')

        # Create playlist_items table (junction table)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            recording_id INTEGER,
            position INTEGER,
            FOREIGN KEY (playlist_id) REFERENCES playlists (id)
                ON DELETE CASCADE,
            FOREIGN KEY (recording_id) REFERENCES recordings (id)
                ON DELETE CASCADE
        )
        ''')

        # Create settings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT
        )
        ''')

        self.conn.commit()

    def add_recording(self, title, filepath, description="", duration=0, cover_art=None):
        """Add a new recording to the database."""
        date_created = datetime.now().isoformat()

        self.cursor.execute('''
        INSERT INTO recordings (title, description, filepath, duration, date_created, cover_art)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, filepath, duration, date_created, cover_art))

        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_recordings(self):
        """Retrieve all recordings from the database."""
        self.cursor.execute('''
        SELECT id, title, description, filepath, duration, date_created, cover_art
        FROM recordings
        ORDER BY date_created DESC
        ''')

        return self.cursor.fetchall()

    def get_recording(self, recording_id):
        """Get a specific recording by ID."""
        self.cursor.execute('''
        SELECT id, title, description, filepath, duration, date_created, cover_art
        FROM recordings
        WHERE id = ?
        ''', (recording_id,))

        return self.cursor.fetchone()

    def update_recording(self, recording_id, title=None, description=None, filepath=None,
                         duration=None, cover_art=None):
        """Update an existing recording's details."""
        # Get current values
        current = self.get_recording(recording_id)
        if not current:
            return False

        # Use current values for any parameters not provided
        title = title if title is not None else current[1]
        description = description if description is not None else current[2]
        filepath = filepath if filepath is not None else current[3]
        duration = duration if duration is not None else current[4]
        cover_art = cover_art if cover_art is not None else current[6]

        self.cursor.execute('''
        UPDATE recordings
        SET title = ?, description = ?, filepath = ?, duration = ?, cover_art = ?
        WHERE id = ?
        ''', (title, description, filepath, duration, cover_art, recording_id))

        self.conn.commit()
        return True

    def delete_recording(self, recording_id):
        """Delete a recording from the database."""
        # First, remove from any playlists
        self.cursor.execute('''
        DELETE FROM playlist_items
        WHERE recording_id = ?
        ''', (recording_id,))

        # Then delete the recording
        self.cursor.execute('''
        DELETE FROM recordings
        WHERE id = ?
        ''', (recording_id,))

        self.conn.commit()
        return True

    def create_playlist(self, name, description=""):
        """Create a new playlist."""
        date_created = datetime.now().isoformat()

        self.cursor.execute('''
        INSERT INTO playlists (name, description, date_created)
        VALUES (?, ?, ?)
        ''', (name, description, date_created))

        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_playlists(self):
        """Retrieve all playlists with count of recordings."""
        self.cursor.execute('''
        SELECT p.id, p.name, p.description, p.date_created,
            (SELECT COUNT(*) FROM playlist_items WHERE playlist_id = p.id) as recording_count
        FROM playlists p
        ORDER BY p.date_created DESC
        ''')

        return self.cursor.fetchall()

    def get_playlist(self, playlist_id):
        """Get a specific playlist by ID."""
        self.cursor.execute('''
        SELECT id, name, description, date_created
        FROM playlists
        WHERE id = ?
        ''', (playlist_id,))

        return self.cursor.fetchone()

    def get_playlist_recordings(self, playlist_id):
        """Get all recordings in a playlist, ordered by position."""
        self.cursor.execute('''
        SELECT r.id, r.title, r.description, r.filepath, r.duration, r.date_created, r.cover_art, pi.position
        FROM recordings r
        JOIN playlist_items pi ON r.id = pi.recording_id
        WHERE pi.playlist_id = ?
        ORDER BY pi.position
        ''', (playlist_id,))

        return self.cursor.fetchall()

    def add_recording_to_playlist(self, playlist_id, recording_id, position=None):
        """Add a recording to a playlist."""
        # If position is not specified, add to the end
        if position is None:
            self.cursor.execute('''
            SELECT COALESCE(MAX(position) + 1, 0)
            FROM playlist_items
            WHERE playlist_id = ?
            ''', (playlist_id,))
            position = self.cursor.fetchone()[0]

        # Check if the recording is already in the playlist
        self.cursor.execute('''
        SELECT id FROM playlist_items
        WHERE playlist_id = ? AND recording_id = ?
        ''', (playlist_id, recording_id))

        if self.cursor.fetchone():
            # If already exists, just update the position
            self.cursor.execute('''
            UPDATE playlist_items
            SET position = ?
            WHERE playlist_id = ? AND recording_id = ?
            ''', (position, playlist_id, recording_id))
        else:
            # Otherwise, insert a new entry
            self.cursor.execute('''
            INSERT INTO playlist_items (playlist_id, recording_id, position)
            VALUES (?, ?, ?)
            ''', (playlist_id, recording_id, position))

        self.conn.commit()
        return True

    def remove_recording_from_playlist(self, playlist_id, recording_id):
        """Remove a recording from a playlist."""
        self.cursor.execute('''
        DELETE FROM playlist_items
        WHERE playlist_id = ? AND recording_id = ?
        ''', (playlist_id, recording_id))

        # Reorder positions to maintain sequence
        self.cursor.execute('''
        UPDATE playlist_items
        SET position = (
            SELECT COUNT(*)
            FROM playlist_items pi2
            WHERE pi2.playlist_id = playlist_items.playlist_id
            AND pi2.id <= playlist_items.id
            AND pi2.id != playlist_items.id
        )
        WHERE playlist_id = ?
        ''', (playlist_id,))

        self.conn.commit()
        return True

    def update_playlist(self, playlist_id, name=None, description=None):
        """Update a playlist's details."""
        current = self.get_playlist(playlist_id)
        if not current:
            return False

        name = name if name is not None else current[1]
        description = description if description is not None else current[2]

        self.cursor.execute('''
        UPDATE playlists
        SET name = ?, description = ?
        WHERE id = ?
        ''', (name, description, playlist_id))

        self.conn.commit()
        return True

    def delete_playlist(self, playlist_id):
        """Delete a playlist and its items."""
        # Due to ON DELETE CASCADE, playlist items will be deleted automatically
        self.cursor.execute('''
        DELETE FROM playlists
        WHERE id = ?
        ''', (playlist_id,))

        self.conn.commit()
        return True

    def reorder_playlist(self, playlist_id, recording_id, new_position):
        """Change the position of a recording within a playlist."""
        # Get the current position
        self.cursor.execute('''
        SELECT position FROM playlist_items
        WHERE playlist_id = ? AND recording_id = ?
        ''', (playlist_id, recording_id))

        result = self.cursor.fetchone()
        if not result:
            return False

        current_position = result[0]

        # Update positions of other items
        if new_position > current_position:
            # Moving down, shift items up
            self.cursor.execute('''
            UPDATE playlist_items
            SET position = position - 1
            WHERE playlist_id = ? AND position > ? AND position <= ?
            ''', (playlist_id, current_position, new_position))
        else:
            # Moving up, shift items down
            self.cursor.execute('''
            UPDATE playlist_items
            SET position = position + 1
            WHERE playlist_id = ? AND position >= ? AND position < ?
            ''', (playlist_id, new_position, current_position))

        # Update the position of the target item
        self.cursor.execute('''
        UPDATE playlist_items
        SET position = ?
        WHERE playlist_id = ? AND recording_id = ?
        ''', (new_position, playlist_id, recording_id))

        self.conn.commit()
        return True

    def set_setting(self, key, value):
        """Set or update a setting."""
        self.cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
        ''', (key, value))

        self.conn.commit()

    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        self.cursor.execute('''
        SELECT value FROM settings
        WHERE key = ?
        ''', (key,))

        result = self.cursor.fetchone()
        return result[0] if result else default

    def search_recordings(self, search_term):
        """Search recordings by title or description."""
        search_term = f"%{search_term}%"

        self.cursor.execute('''
        SELECT id, title, description, filepath, duration, date_created, cover_art
        FROM recordings
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY date_created DESC
        ''', (search_term, search_term))

        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
