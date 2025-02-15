import pytest
import requests

# Base URL for your API
BASE_URL = 'http://localhost:8000/api'

def test_create_study_session_success():
    # Assuming you have valid group and study activity IDs
    payload = {
        'group_id': 1,  # Replace with a valid group ID
        'study_activity_id': 1  # Replace with a valid study activity ID
    }
    
    response = requests.post(f'{BASE_URL}/study-sessions', json=payload)
    
    assert response.status_code == 201
    assert 'session_id' in response.json()
    assert response.json()['message'] == 'Study session created successfully'

def test_create_study_session_missing_fields():
    payload = {}
    
    response = requests.post(f'{BASE_URL}/study-sessions', json=payload)
    
    assert response.status_code == 400
    assert 'error' in response.json()
    assert 'Missing required fields' in response.json()['error']

def test_create_study_session_nonexistent_group():
    payload = {
        'group_id': 9999,  # Non-existent group ID
        'study_activity_id': 1
    }
    
    response = requests.post(f'{BASE_URL}/study-sessions', json=payload)
    
    assert response.status_code == 404
    assert 'error' in response.json()
    assert 'Group not found' in response.json()['error']

def test_create_study_session_nonexistent_activity():
    payload = {
        'group_id': 1,
        'study_activity_id': 9999  # Non-existent activity ID
    }
    
    response = requests.post(f'{BASE_URL}/study-sessions', json=payload)
    
    assert response.status_code == 404
    assert 'error' in response.json()
    assert 'Study activity not found' in response.json()['error']