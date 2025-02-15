import pytest
import requests

# Base URL for your API
BASE_URL = 'http://localhost:8000/api'

def test_get_study_activities():
    """
    Test retrieving all study activities
    """
    response = requests.get(f'{BASE_URL}/study-activities')
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Check if each activity has the required fields
    for activity in data:
        assert 'id' in activity
        assert 'title' in activity
        assert 'launch_url' in activity
        assert 'preview_url' in activity

def test_get_single_study_activity(valid_study_activity_id):
    """
    Test retrieving a single study activity by ID
    """
    response = requests.get(f'{BASE_URL}/study-activities/{valid_study_activity_id}')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'id' in data
    assert 'title' in data
    assert 'launch_url' in data
    assert 'preview_url' in data
    assert data['id'] == valid_study_activity_id

def test_get_nonexistent_study_activity():
    """
    Test retrieving a non-existent study activity
    """
    # Assuming 99999 is an ID that doesn't exist
    response = requests.get(f'{BASE_URL}/study-activities/99999')
    
    assert response.status_code == 404
    
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Activity not found'

def test_get_study_activity_sessions(valid_study_activity_id):
    """
    Test retrieving sessions for a study activity
    """
    response = requests.get(f'{BASE_URL}/study-activities/{valid_study_activity_id}/sessions')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'items' in data
    assert 'total' in data
    assert 'page' in data
    assert 'per_page' in data
    assert 'total_pages' in data
    
    # Check pagination parameters
    assert data['page'] == 1
    assert data['per_page'] == 10
    
    # Check session items
    for session in data['items']:
        assert 'id' in session
        assert 'group_id' in session
        assert 'group_name' in session
        assert 'activity_id' in session
        assert 'activity_name' in session
        assert 'start_time' in session
        assert 'end_time' in session
        assert 'review_items_count' in session

def test_get_study_activity_sessions_pagination(valid_study_activity_id):
    """
    Test pagination for study activity sessions
    """
    # Test custom page and per_page parameters
    response = requests.get(f'{BASE_URL}/study-activities/{valid_study_activity_id}/sessions', 
                             params={'page': 2, 'per_page': 5})
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['page'] == 2
    assert data['per_page'] == 5

def test_get_nonexistent_activity_sessions():
    """
    Test retrieving sessions for a non-existent study activity
    """
    response = requests.get(f'{BASE_URL}/study-activities/99999/sessions')
    
    assert response.status_code == 404
    
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Activity not found'

def test_get_study_activity_launch_data(valid_study_activity_id):
    """
    Test retrieving launch data for a study activity
    """
    response = requests.get(f'{BASE_URL}/study-activities/{valid_study_activity_id}/launch')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'activity' in data
    assert 'groups' in data
    
    # Check activity details
    activity = data['activity']
    assert 'id' in activity
    assert 'title' in activity
    assert 'launch_url' in activity
    assert 'preview_url' in activity
    assert activity['id'] == valid_study_activity_id
    
    # Check groups
    for group in data['groups']:
        assert 'id' in group
        assert 'name' in group

def test_get_nonexistent_activity_launch_data():
    """
    Test retrieving launch data for a non-existent study activity
    """
    response = requests.get(f'{BASE_URL}/study-activities/99999/launch')
    
    assert response.status_code == 404
    
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Activity not found'
