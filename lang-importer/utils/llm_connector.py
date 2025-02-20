import requests
import json
from typing import List, Dict
import os

class OllamaLLMConnector:
    def __init__(self, endpoint: str = "http://ollama-server:8008/api/generate", model: str = "llama3.2:1b"):
        self.endpoint = endpoint
        self.model = model

    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using Ollama LLM
        
        Args:
            prompt (str): Input prompt for text generation
            max_tokens (int): Maximum number of tokens to generate
        
        Returns:
            str: Generated text response
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to LLM: {e}")
            return ""

    def parse_json_from_response(self, response: str) -> List[Dict[str, str]]:
        """
        Extract JSON from LLM response
        
        Args:
            response (str): LLM text response
        
        Returns:
            List[Dict[str, str]]: Parsed vocabulary list
        """
        try:
            # Try to extract JSON between first [ and last ]
            start = response.find('[')
            end = response.rfind(']') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            print("Could not parse JSON from response")
            return []
