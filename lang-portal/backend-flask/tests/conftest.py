import pytest
import sqlite3

@pytest.fixture(scope='session')
def db_connection():
    # Setup: Connect to your test database
    conn = sqlite3.connect('words.db')

    yield conn
    # Teardown: Close the connection
    conn.close()

@pytest.fixture
def valid_group_id(db_connection):
    # Fetch a valid group ID for testing
    cursor = db_connection.cursor()
    cursor.execute('SELECT id FROM groups LIMIT 1')
    group_id = cursor.fetchone()[0]
    return group_id

@pytest.fixture
def valid_word_id(db_connection):
    # Fetch a valid word ID for testing
    cursor = db_connection.cursor()
    cursor.execute('SELECT id FROM words LIMIT 1')
    word_id = cursor.fetchone()[0]
    return word_id

@pytest.fixture
def valid_study_activity_id(db_connection):
    # Fetch a valid study activity ID for testing
    cursor = db_connection.cursor()
    cursor.execute('SELECT id FROM study_activities LIMIT 1')
    activity_id = cursor.fetchone()[0]
    return activity_id