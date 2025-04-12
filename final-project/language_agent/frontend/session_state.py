import streamlit as st
import logging

from language_agent.tools import S3DownloaderTool, S3DownloaderToolConfig
from language_agent.backend.config import AgentConfig

logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initializes the Streamlit session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
        logger.info("Session state: 'agent' initialized.")
    if 'current_response' not in st.session_state:
        st.session_state.current_response = None # Store the latest UIOutputSchema
        logger.info("Session state: 'current_response' initialized to None.")
    if 'exercise_started' not in st.session_state:
        st.session_state.exercise_started = False
        logger.info("Session state: 'exercise_started' initialized to False.")
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = "easy" # Default difficulty
        logger.info("Session state: 'difficulty' initialized to 'easy'.")
    if 'topic' not in st.session_state:
        st.session_state.topic = "" # Default topic
        logger.info("Session state: 'topic' initialized to empty string.")
    if 'image' not in st.session_state:
        st.session_state.image = None
        logger.info("Session state: 'image' initialized to None.")
    if 'audio' not in st.session_state:
        st.session_state.audio = None
        logger.info("Session state: 'audio' initialized to None.")
    if 's3_dl_tool' not in st.session_state:
        st.session_state.s3_dl_tool = S3DownloaderTool(
            S3DownloaderToolConfig(
                aws_access_key_id=AgentConfig.aws_access_key_id,
                aws_secret_access_key=AgentConfig.aws_secret_access_key,
                aws_region=AgentConfig.aws_region
            )
        )
