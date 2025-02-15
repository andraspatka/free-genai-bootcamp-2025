import pytest
import requests

# Base URL for your API
BASE_URL = 'http://localhost:8000/api'

def test_get_words():
    """
    Test retrieving words with default pagination
    """
    response = requests.get(f'{BASE_URL}/words')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'words' in data
    assert 'total_pages' in data
    assert 'current_page' in data
    assert 'total_words' in data
    
    # Check word structure
    for word in data['words']:
        assert 'id' in word
        assert 'english' in word
        assert 'italian' in word
        assert 'correct_count' in word
        assert 'wrong_count' in word

def test_get_words_pagination():
    """
    Test words pagination with custom parameters
    """
    response = requests.get(f'{BASE_URL}/words', params={
        'page': 2,
        'sort_by': 'correct_count',
        'order': 'desc'
    })
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['current_page'] == 2

def test_get_single_word(valid_word_id):
    """
    Test retrieving a single word by ID
    """
    response = requests.get(f'{BASE_URL}/words/{valid_word_id}')
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'word' in data
    
    word = data['word']
    assert 'id' in word
    assert 'english' in word
    assert 'italian' in word
    assert 'correct_count' in word
    assert 'wrong_count' in word
    assert 'groups' in word
    
    # Check groups structure
    for group in word['groups']:
        assert 'id' in group
        assert 'name' in group

def test_get_nonexistent_word():
    """
    Test retrieving a non-existent word
    """
    response = requests.get(f'{BASE_URL}/words/99999')
    
    assert response.status_code == 404
    
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Word not found'
