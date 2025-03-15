import json
from backend.chat import BedrockChat

JSON_OUTPUT_GUARDRAIL = """
CRITICAL: Output the response in JSON format and output only the JSON object without any extra text.
"""

class LanguagePrompts:
    def __init__(self):
        self.chat_client = BedrockChat()


    def generate_sentence(self, word: str) -> str:
        """Generate a simple sentence using the specified word."""
        prompt = f"""
        Generate a simple sentence using the following word: {word}. 
        The grammar should be scoped to English CEFR A1 grammar.
        {JSON_OUTPUT_GUARDRAIL}
        """ + """
        JSON format:
        {
            "sentence": str
        }
        """
        
        try:
            response = self.chat_client.generate_response(prompt)
            response = json.loads(response)
            return response.get('sentence', '')
        except Exception as e:
            print(f"Error generating sentence: {str(e)}")
            return ""


    def grade_translation(self, sentence_en: str, sentence_it: str) -> json:
        """Grade the translation from English to Italian."""
        prompt = f"""
        Grade the following translation:
        English: {sentence_en}
        Italian: {sentence_it}
        Provide feedback about the translation and a score between 0 and 100 based on how good the translation was.
        {JSON_OUTPUT_GUARDRAIL}
        Ignore errors regarding accents.
        """ + """
        JSON format:
        {
            "feedback": str,
            "is_correct": boolean,
            "score": int
        }
        """
        
        try:
            response = self.chat_client.generate_response(prompt)
            return json.loads(response)
        except Exception as e:
            print(f"Error grading translation: {str(e)}")
            return {"feedback": "Error occurred while grading.", "score": 0}


# Example usage
if __name__ == "__main__":
    prompts = LanguagePrompts()
    sentence = prompts.generate_sentence("libro")
    print(f"Generated Sentence: {sentence}")
    
    feedback = prompts.grade_translation("The book is on the table.", "Il libro è sul tavolo.")
    print(f"Feedback: {json.dumps(feedback, indent=2)}")
