"""
This client should have the possibility to send out requests to:
Get word groups first:
    http://localhost:8000/api/groups -> Returns a list of word groups with pagination:
    example response:
    {
        "current_page": 1,
        "groups": [
            {
                "group_name": "Core Adjectives",
                "id": 5,
                "word_count": 27
            },
            {
                "group_name": "Core Verbs",
                "id": 1,
                "word_count": 27
            },
            {
                "group_name": "Core Verbs",
                "id": 2,
                "word_count": 0
            }
        ],
        "total_pages": 1
    }
Parse the response. Based on the previous response of the word group IDs, get the words:
Get the words based on the word group id
    http://localhost:8000/api/groups/:word_group_id/words -> Returns a list of words with pagination
    {
        "current_page": 1,
        "total_pages": 3,
        "words": [
            {
                "correct_count": 0,
                "english": "bitter",
                "id": 41,
                "italian": "amaro",
                "wrong_count": 0
            },
            {
                "correct_count": 0,
                "english": "beautiful",
                "id": 52,
                "italian": "bellissimo",
                "wrong_count": 0
            }
        ]
    }
"""
import requests
import random


class LangPortalClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_groups(self, page=1):
        """Retrieve language groups from the portal."""
        try:
            response = requests.get(f"{self.base_url}/groups")
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching groups: {str(e)}")
            return None


    def get_words(self, group_id):
        """Retrieve words for a specific group."""
        try:
            response = requests.get(f"{self.base_url}/groups/{group_id}/words")
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching words for group {group_id}: {str(e)}")
            return None


    def get_random_word(self):
        """Retrieve a random word from the portal."""
        groups = self.get_groups()
        if groups:
            if groups['total_pages'] > 0:
                group_ids = [g['id'] for g in groups['groups'] if g['word_count'] > 0]
                random_group_id = random.randint(0, len(group_ids) - 1)

                words = self.get_words(group_ids[random_group_id])

                if words:
                    random_word = random.randint(0, len(words) - 1)

                    return words['words'][random_word]['english']
                else:
                    print("No words found in the group.")
            else:
                print("No groups found with words.")
        return None


# Example usage
if __name__ == "__main__":
    client = LangPortalClient("http://lang-portal-api:8000/api")
    groups = client.get_groups()
    if groups:
        print(groups)
        if groups['total_pages'] > 0:
            first_group_id = groups['groups'][0]['id']
            words = client.get_words(first_group_id)
            print(words)
    
    random_word = client.get_random_word()
    print(f"Random word is {random_word}")
