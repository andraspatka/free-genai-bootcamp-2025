import os
from dataclasses import dataclass
from typing import Set


def get_env(key: str) -> str:
    """Retrieve env var with key param: key or raise error"""
    val = os.getenv(key)
    if not val:
        raise ValueError(f"{key} not found in environment variables.")
    return val


@dataclass
class AgentConfig:
    """Configuration for the chat application"""

    api_key: str = get_env("OPENAI_API_KEY")
    aws_access_key_id: str = get_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = get_env("AWS_SECRET_ACCESS_KEY")
    aws_region: str = get_env("AWS_REGION")
    s3_bucket: str = get_env("S3_BUCKET_NAME")
    model: str = "gpt-4o-mini"
    target_language: str = "Italian"

    def __init__(self):
        # Prevent instantiation
        raise TypeError("ChatConfig is not meant to be instantiated")