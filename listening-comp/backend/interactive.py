import os
import json
import random
from backend.chat import BedrockChat


class ListeningComprehension:
    def __init__(self):
        self.bedrock_chat = BedrockChat()
        self.data_directory = os.path.join("data", "structured")


    def get_text(self) -> str:
        """Randomly get a file from data/structured and return the 'transcript' value."""
        # Get a list of all JSON files in the data/structured directory
        files = [f for f in os.listdir(self.data_directory) if f.endswith('.json')]
        
        if not files:
            raise FileNotFoundError("No JSON files found in the data/structured directory.")
        
        # Randomly select a file
        selected_file = random.choice(files)
        file_path = os.path.join(self.data_directory, selected_file)
        
        # Parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.loads(json.load(f)) # text contains escaped characters, need to load it twice
        
        return data, selected_file.replace(".json", "")


    def generate_questions(self, text: str) -> json:
        """Generate questions based on the provided text using the BedrockChat client."""
        # Assuming the BedrockChat client has a method to generate questions
        questions_data = self.bedrock_chat.generate_response(f"""
            The following text is the transcript of an Italian A1 level listening exercise:
            {text}

            I want you to act like a language teacher that wants to accurately measure whether the students
            who have listened to this text, understand the content and the concepts presented.
            
            Generate 4 questions based on the content of the text. 
            Please output a JSON object with the following structure:""" +
            """{
                \"questions\": [
                    {
                        \"question\": str,
                        \"options\": [
                            \"number\": int,
                            \"option\": str,
                            \"is_correct\": bool,
                            \"feedback\": str
                        ],
                        \"correct_answer\": int,
                    },
                    ...
                ]
            }
            Please output only the generated JSON object. The questions are:
        """)
        print(questions_data)
        return json.loads(questions_data)


if __name__ == "__main__":
    listening_comprehension = ListeningComprehension()
    data, video_id = listening_comprehension.get_text()
    print(data)
    print(video_id)
    questions = listening_comprehension.generate_questions(data["transcript"])
    print(questions)