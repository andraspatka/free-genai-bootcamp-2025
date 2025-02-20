import json
from typing import List, Dict
from .llm_connector import OllamaLLMConnector

class VocabGenerator:
    def __init__(self, llm_connector: OllamaLLMConnector):
        self.llm_connector = llm_connector

    def generate_vocab(self, word_group: str, language: str = 'Italian', num_words: int = 10) -> List[Dict[str, str]]:
        """
        Generate vocabulary for a specific word group
        
        Args:
            word_group (str): Type of words to generate (e.g., 'adjectives', 'verbs')
            language (str): Target language for translation
            num_words (int): Number of words to generate
        
        Returns:
            List[Dict[str, str]]: Generated vocabulary list
        """
        prompt = f"""Generate a list of {num_words} {word_group} in English with their {language} translations. 
        Provide the response in a valid JSON format like this:
        [
            {{"english": "word1", "{language.lower()}": "translation1"}},
            {{"english": "word2", "{language.lower()}": "translation2"}}
        ]
        Ensure the words are common and useful for language learners."""

        response = self.llm_connector.generate_text(prompt)
        vocab_list = self.llm_connector.parse_json_from_response(response)
        
        return vocab_list

    def export_to_json(self, vocab_list: List[Dict[str, str]], filename: str):
        """
        Export vocabulary list to a JSON file
        
        Args:
            vocab_list (List[Dict[str, str]]): Vocabulary to export
            filename (str): Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(vocab_list, f, ensure_ascii=False, indent=4)
        print(f"Vocabulary exported to {filename}")
