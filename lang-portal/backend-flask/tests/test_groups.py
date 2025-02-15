import pytest
import requests

# Base URL for your API
BASE_URL = 'http://localhost:8000/api'

def test_get_groups():
    """
    Test retrieving groups with default pagination
    """
    response = requests.get(f'{BASE_URL}/groups')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'groups' in data
    assert 'total_pages' in data
    assert 'current_page' in data
    
    # Check group structure
    for group in data['groups']:
        assert 'id' in group
        assert 'group_name' in group
        assert 'word_count' in group

def test_get_groups_pagination():
    """
    Test groups pagination with custom parameters
    """
    response = requests.get(f'{BASE_URL}/groups', params={
        'page': 2,
        'sort_by': 'words_count',
        'order': 'desc'
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['current_page'] == 2

def test_get_single_group(valid_group_id):
    """
    Test retrieving a single group by ID
    """
    response = requests.get(f'{BASE_URL}/groups/{valid_group_id}')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'id' in data
    assert 'group_name' in data
    assert 'word_count' in data
    assert data['id'] == valid_group_id

def test_get_nonexistent_group():
    """
    Test retrieving a non-existent group
    """
    response = requests.get(f'{BASE_URL}/groups/99999')
    
    assert response.status_code == 404
    
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Group not found'

def test_get_group_words(valid_group_id):
    """
    Test retrieving words for a group
    """
    response = requests.get(f'{BASE_URL}/groups/{valid_group_id}/words')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'words' in data
    assert 'total_pages' in data
    assert 'current_page' in data
    
    # Check word structure
    for word in data['words']:
        assert 'id' in word
        assert 'english' in word
        assert 'italian' in word
        assert 'correct_count' in word
        assert 'wrong_count' in word

def test_get_group_words_pagination(valid_group_id):
    """
    Test group words pagination with custom parameters
    """
    response = requests.get(f'{BASE_URL}/groups/{valid_group_id}/words', params={
        'page': 2,
        'sort_by': 'correct_count',
        'order': 'desc'
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['current_page'] == 2

def test_get_nonexistent_group_words():
    """
    Test retrieving words for a non-existent group
    """
    response = requests.get(f'{BASE_URL}/groups/99999/words')
    
    assert response.status_code == 404
    
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Group not found'

def test_get_group_words_raw(valid_group_id):
    """
    Test retrieving raw words for a group
    """
    response = requests.get(f'{BASE_URL}/groups/{valid_group_id}/words/raw')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'words' in data
    assert 'count' in data
    assert data['count'] == len(data['words'])
    
    # Check word structure
    for word in data['words']:
        assert 'id' in word
        assert 'english' in word
        assert 'italian' in word

def test_get_group_study_sessions(valid_group_id):
    """
    Test retrieving study sessions for a group
    """
    response = requests.get(f'{BASE_URL}/groups/{valid_group_id}/study_sessions')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'total_pages' in data
    assert 'current_page' in data
    assert 'study_sessions' in data
    
    # Check session structure
    for session in data['study_sessions']:
        assert 'id' in session
        assert 'group_id' in session
        assert 'study_activity_id' in session
        assert 'start_time' in session
        assert 'end_time' in session
        assert 'activity_name' in session
        assert 'group_name' in session
        assert 'review_items_count' in session

def test_get_group_study_sessions_pagination(valid_group_id):
    """
    Test group study sessions pagination with custom parameters
    """
    response = requests.get(f'{BASE_URL}/groups/{valid_group_id}/study_sessions', params={
        'page': 2,
        'sort_by': 'startTime',
        'order': 'desc'
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['current_page'] == 2
