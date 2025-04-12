import streamlit as st
from language_agent.backend.schemas import QuizSchema

from language_agent.backend.config import AgentConfig # For default language
from language_agent.backend.schemas import UIOutputSchema, AgentInputSchema

from language_agent.backend.agent import LanguageExerciseAgent

import logging


logger = logging.getLogger(__name__)




def display_quiz():
    """Displays quiz questions and options."""
    if not st.session_state.quiz:
        logger.error("No quiz available for this exercise.")
        return

    if st.session_state.quiz:
        st.text(st.session_state.quiz[0].question)
        options = [q.option for q in st.session_state.quiz[0].options]
        selected = st.radio("Choose your answer:", options, key="interactive_exercise_question")
        st.session_state.quiz_selection = selected

    if st.button("Check"): 
        st.subheader("Feedback")
        if st.session_state.quiz_selection:
            feedback = [
                q.feedback
                for q in st.session_state.quiz[0].options 
                if q.option == st.session_state.quiz_selection
            ][0]
            correct_answer = [
                q.option
                for q in st.session_state.quiz[0].options 
                if q.is_correct
            ][0]
            is_correct = st.session_state.quiz_selection == correct_answer
            st.text_area(
                label="Feedback",
                value=f"""
                    Your choice is {st.session_state.quiz_selection}, it's {'correct' if is_correct else 'unfortunately wrong'}
                    Correct answer: {correct_answer}
                    Feedback: {feedback}
                """,
                height=400,
                disabled=True
            )


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
                    except Exception as e:
                        logger.error(f"Error initializing or running agent: {e}", exc_info=True)
                        st.error(f"Error initializing or running agent: {e}")
                        st.session_state.exercise_started = False # Allow retry

def render_chat_messages():
    logging.info("Rendering chat messages called")
    if st.session_state.agent:
        # Display chat messages
        for message in st.session_state.agent.get_message_history():
            with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
    else:
        st.markdown("No agent in state")


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
