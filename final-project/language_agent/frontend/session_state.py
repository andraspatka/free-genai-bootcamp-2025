import streamlit as st
import logging

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
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0 # To reset chat input
        logger.info("Session state: 'input_key' initialized to 0.")
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = "easy" # Default difficulty
        logger.info("Session state: 'difficulty' initialized to 'easy'.")
    if 'topic' not in st.session_state:
        st.session_state.topic = "" # Default topic
        logger.info("Session state: 'topic' initialized to empty string.")
