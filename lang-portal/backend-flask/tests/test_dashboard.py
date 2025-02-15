import pytest
import requests

# Base URL for your API
BASE_URL = 'http://localhost:8000'

def test_get_recent_session():
    """
    Test retrieving the most recent study session
    """
    response = requests.get(f'{BASE_URL}/dashboard/recent-session')
    
    assert response.status_code == 200
    
    data = response.json()
    
    # The response can be None if no sessions exist
    if data is not None:
        assert 'id' in data
        assert 'group_id' in data
        assert 'activity_name' in data
        assert 'created_at' in data
        assert 'correct_count' in data
        assert 'wrong_count' in data

def test_get_study_stats():
    """
    Test retrieving dashboard study statistics
    """
    response = requests.get(f'{BASE_URL}/dashboard/stats')
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check for all expected keys in the stats
    expected_keys = [
        'total_vocabulary',
        'total_words_studied',
        'mastered_words',
        'success_rate',
        'total_sessions',
        'active_groups',
        'current_streak'
    ]
    
    for key in expected_keys:
        assert key in data
    
    # Validate types and ranges for numeric values
    assert isinstance(data['total_vocabulary'], int)
    assert isinstance(data['total_words_studied'], int)
    assert isinstance(data['mastered_words'], int)
    assert 0 <= data['success_rate'] <= 1
    
    assert isinstance(data['total_sessions'], int)
    assert isinstance(data['active_groups'], int)
    assert isinstance(data['current_streak'], int)
    
    # Ensure counts are non-negative
    assert data['total_vocabulary'] >= 0
    assert data['total_words_studied'] >= 0
    assert data['mastered_words'] >= 0
    assert data['total_sessions'] >= 0
    assert data['active_groups'] >= 0
    assert data['current_streak'] >= 0
