import streamlit as st
from typing import Optional, Dict, Any

import json
import os

from backend.chat import BedrockChat


class TranscriptStructurer:
    def __init__(self):
        """Initialize Bedrock chat client"""
        self.chat_client = BedrockChat()

    def structure_transcript(self, transcript: str) -> Optional[str]:
        """Generate a response using Amazon Bedrock"""
        prompt = '''
            I have the following transcript from a youtube video which is of an Italian listening comprehension test
            level A1.
            Please take this transcript and extract the parts which are strictly for the listening exercise only.
            If the transcript is not exactly correct Italian, then fix it so the sentences all make sense and are correct
            both in terms of grammar and meaning. Please structure the transcript into proper sentences as well, in case 
            the punctuation is not correct or would result in very long sentences.
            Please output the result in the following JSON format:
            {
                "transcript": "the transcript",
                "english_translation": "the english translation"
            }
            Don't output anything else other than the JSON. The output of this prompt will be used by a script later one.
            If the text contains anything else other than the JSON output, then the script will fail!
        
            The transcript is: 
            ''' + transcript

        structured_data = self.chat_client.generate_response(prompt)

        return structured_data

    def save_to_file(self, structured_data: str, video_id: str) -> None:
        os.makedirs("data/structured", exist_ok=True)
        with open(f"data/structured/{video_id}.json", "w", encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=4)

