import os
from kivy.app import App
import sqlite3


def get_db_path():
    return os.path.join(App.get_running_app().user_data_dir, 'audio_database.db')


def init_db():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS RECORDINGS (
            ID INTEGER PRIMARY KEY,
            TITLE TEXT,
            DESCRIPTION TEXT,
            DATE TEXT,
            COVER_ART_PATH TEXT,
            AUDIO_PATH TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PLAYLISTS (
            ID INTEGER PRIMARY KEY,
            NAME TEXT,
            DESCRIPTION TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PLAYLIST_RECORDINGS (
            PLAYLIST_ID INTEGER,
            RECORDING_ID INTEGER,
            ORDER_NUM INTEGER,
            PRIMARY KEY (PLAYLIST_ID, RECORDING_ID),
            FOREIGN KEY (PLAYLIST_ID) REFERENCES PLAYLISTS(ID),
            FOREIGN KEY (RECORDING_ID) REFERENCES RECORDINGS(ID)
        )
    ''')
    # add_recording('Ma Bishla Hahatula - Try', 'trying', '2025-03-05', None, './data/recordings/tryout.wav')
    cursor.execute(
        "INSERT INTO RECORDINGS (TITLE, DESCRIPTION, DATE, COVER_ART_PATH, AUDIO_PATH) VALUES (?, ?, ?, ?, ?)",
        ('Ma Bishla Hahatula - Try', 'trying', '2025-03-05', None, './data/recordings/tryout.wav'))
    conn.commit()
    conn.close()


def add_recording(title, description, date, cover_art_path, audio_path):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO RECORDINGS (TITLE, DESCRIPTION, DATE, COVER_ART_PATH, AUDIO_PATH) VALUES (?, ?, ?, ?, ?)",
        (title, description, date, cover_art_path, audio_path))
    conn.commit()
    conn.close()


def get_all_recordings():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, audio_path FROM recordings")
    recordings = cursor.fetchall()
    conn.close()
    return recordings


def create_playlist(name, description):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PLAYLISTS (NAME, DESCRIPTION) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()


def get_all_playlists():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PLAYLISTS")
    playlists = cursor.fetchall()
    conn.close()
    return playlists


def add_recording_to_playlist(playlist_id, recording_id, order_num):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PLAYLIST_RECORDINGS (PLAYLIST_ID, RECORDING_ID, ORDER_NUM) VALUES (?, ?, ?)",
                   (playlist_id, recording_id, order_num))
    conn.commit()
    conn.close()


def get_playlist_recordings(playlist_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "SELECT R.* FROM RECORDINGS R JOIN PLAYLIST_RECORDINGS PR ON R.ID = PR.RECORDING_ID WHERE PR.PLAYLIST_ID = ? ORDER BY PR.ORDER_NUM",
        (playlist_id,))
    recordings = cursor.fetchall()
    conn.close()
    return recordings


def update_playlist(playlist_id, name, description):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("UPDATE PLAYLISTS SET NAME = ?, DESCRIPTION = ? WHERE ID = ?", (name, description, playlist_id))
    conn.commit()
    conn.close()


def delete_playlist(playlist_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    conn.commit()
    conn.close()


def reorder_playlist_recordings(playlist_id, recording_ids):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    for order_num, rec_id in enumerate(recording_ids):
        cursor.execute("UPDATE playlist_recordings SET order_num = ? WHERE playlist_id = ? AND recording_id = ?", (order_num, playlist_id, rec_id))
    conn.commit()
    conn.close()


