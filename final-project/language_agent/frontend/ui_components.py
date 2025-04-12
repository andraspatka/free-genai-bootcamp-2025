import streamlit as st
from language_agent.backend.schemas import QuizSchema

from language_agent.backend.config import AgentConfig # For default language
from language_agent.backend.schemas import UIOutputSchema, AgentInputSchema

from language_agent.backend.agent import LanguageExerciseAgent

import logging


logger = logging.getLogger(__name__)


def display_quiz(quiz_questions: list[QuizSchema]):
    """Displays quiz questions and options."""
    if not quiz_questions:
        return
    for i, quiz in enumerate(quiz_questions):
        st.subheader(f"Question {i+1}")
        st.write(quiz.question)
        if quiz.options:
            options = [opt.option for opt in quiz.options]
            # Using radio buttons for single choice - unique key needed
            selected_option = st.radio(
                f"Options for Question {i+1}",
                options,
                key=f"quiz_{st.session_state.current_response.response_to_user}_{i}" # Key based on response + index
            )
            # Simple display of options - feedback logic could be added if backend provides evaluation
            # chosen_option_schema = next((opt for opt in quiz.options if opt.option == selected_option), None)
            # if chosen_option_schema:
            #     if chosen_option_schema.is_correct:
            #         st.success(f"Feedback: {chosen_option_schema.feedback}")
            #     else:
            #         st.warning(f"Feedback: {chosen_option_schema.feedback}")
        else:
            st.text_input("Your answer:", key=f"quiz_answer_{i}") # Open-ended question

def header():
    with st.container(border=True):
        st.header("Exercise Setup")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            selected_difficulty = st.selectbox(
                "Select Difficulty",
                ("easy", "medium", "hard"),
                index=["easy", "medium", "hard"].index(st.session_state.difficulty) if st.session_state.difficulty else 0,
                key="difficulty_select",
                disabled=st.session_state.exercise_started # Disable after starting
            )
        with col2:
            input_topic = st.text_input(
                "Enter Topic",
                value=st.session_state.topic,
                key="topic_input",
                placeholder=f"e.g., Ordering coffee, Family members, Past tense verbs in {AgentConfig.target_language}",
                disabled=st.session_state.exercise_started # Disable after starting
            )
        with col3:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("🚀 Generate Exercise", key="generate_button", type="primary", use_container_width=True, disabled=st.session_state.exercise_started):
                if not input_topic:
                    st.error("Please enter a topic.")
                else:
                    st.session_state.difficulty = selected_difficulty
                    st.session_state.topic = input_topic
                    st.session_state.current_response = None
                    st.session_state.exercise_started = True
                    st.session_state.input_key += 1 # Reset chat input state

                    logger.info(f"Starting exercise generation. Difficulty: {selected_difficulty}, Topic: {input_topic}")

                    # Initialize Agent
                    try:
                        st.session_state.agent = LanguageExerciseAgent(difficulty=st.session_state.difficulty)
                        logger.info("LanguageExerciseAgent initialized successfully.")
                        initial_request = AgentInputSchema(
                            topic=st.session_state.topic,
                            target_language=AgentConfig.target_language
                        )
                        logger.info(f"Running agent with initial request: {initial_request.model_dump()}")
                        with st.spinner(f"Generating {st.session_state.difficulty} exercise on '{st.session_state.topic}'..."):
                            response: UIOutputSchema = st.session_state.agent.run(initial_request)
                            st.session_state.current_response = response
                            logger.info(f"Agent initial response received: {response.model_dump(exclude={'image_s3', 'audio_s3'})}") # Avoid logging potentially large fields
                            # Add initial agent response to messages
                        st.rerun() # Rerun to update layout based on new state
                    except Exception as e:
                        logger.error(f"Error initializing or running agent: {e}", exc_info=True)
                        st.error(f"Error initializing or running agent: {e}")
                        st.session_state.exercise_started = False # Allow retry

def render_chat_messages():
    if st.session_state.agent:
        # Display chat messages
        for message in st.session_state.agent.get_message_history():
            with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])


def footer():
    if st.session_state.exercise_started:
        st.divider()
        if st.button("🔄 Start New Exercise"):
            logger.info("Resetting session state for new exercise.")
            # Reset state variables
            st.session_state.agent = None
            st.session_state.difficulty = "easy" # Reset to default
        st.session_state.topic = ""
        st.session_state.messages = []
        st.session_state.current_response = None
        st.session_state.exercise_started = False
        st.session_state.input_key += 1 # Reset chat input state
        st.rerun()