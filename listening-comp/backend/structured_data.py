import boto3
import streamlit as st
from typing import Optional, Dict, Any

from backend.chat import BedrockChat


class TranscriptStructurer:
    def __init__(self):
        """Initialize Bedrock chat client"""
        self.chat_client = BedrockChat()

    def structure_transcript(self, transcript: str) -> Optional[str]:
        """Generate a response using Amazon Bedrock"""
        prompt = f'''
            I have the following transcript from a youtube video which is of an Italian listening comprehension test
            level A1.
            It is structured in the following way:
            - Introduction
            - First listening excercise
            - Second listening excercise
            - Third listening excercis
            - Conclusion

            Please take the transcript and restructure it in the specified way. Print out the English translation alongside the italian parts
            The transcript is: {transcript}
        '''

        return self.chat_client.generate_response(prompt)


