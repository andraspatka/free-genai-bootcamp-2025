import streamlit as st
from language_agent.backend.schemas import QuizSchema

from language_agent.backend.config import AgentConfig # For default language
from language_agent.backend.schemas import UIOutputSchema, AgentInputSchema
from language_agent.tools import S3DownloaderTool, S3DownloaderToolConfig, S3DownloaderToolInputSchema

from language_agent.frontend.util import base64_to_pil_image, base64_to_audio
from language_agent.tools import S3DownloaderTool, S3DownloaderToolConfig, S3DownloaderToolInputSchema

from language_agent.backend.agent import LanguageExerciseAgent
from language_agent.backend.schemas import AgentInputSchema, UIOutputSchema, QuizSchema, QuizOptionSchema
from language_agent.backend.config import AgentConfig # For default language

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

def main_content():
    # --- Main Content Area ---
    st.divider()

    chat = st.container()
    logging.info(st.session_state)
    difficulty = st.session_state.difficulty
    logger.info(f"Displaying content for difficulty: {difficulty}")

    # --- Chat Input (Common) ---
    # Place chat input outside the columns to ensure it's always visible when exercise is active
    user_input_value = st.chat_input("Your response:")

    # --- Populate Placeholders based on difficulty ---
    if difficulty == "easy":
        st.subheader("Conversation")
        render_chat_messages()
    elif difficulty in ["medium", "hard"]:
        col_chat, col_resources = chat.columns(2)

        with col_chat:
            st.subheader("Conversation")
            render_chat_messages()

        latest_response = st.session_state.current_response
        with col_resources:
            st.subheader("Resources")
            
            if difficulty == "medium":
                if st.session_state.image is None:
                    s3_path = latest_response.image_s3
                    image_base64 = st.session_state.s3_dl_tool.run(S3DownloaderToolInputSchema(s3_path=s3_path)).file_base64
                    st.session_state.image = base64_to_pil_image(image_base64)
                
                if st.session_state.image:
                    st.image(st.session_state.image, caption="🖼️ Generated Image", use_column_width=True)
                else:
                    st.info("No image available for this exercise.")

            elif difficulty == "hard":
                if st.session_state.audio is None:
                    s3_path = latest_response.audio_s3
                    audio_base64 = st.session_state.s3_dl_tool.run(S3DownloaderToolInputSchema(s3_path=s3_path)).file_base64
                    st.session_state.audio = audio_base64
                
                st.audio(base64_to_audio(st.session_state.audio))

                # Display Quiz
                if st.session_state.quiz is None:
                    st.session_state.quiz = latest_response.quiz
                    
                logger.info("Displaying quiz.")
                display_quiz()


    # --- Handle User Input Submission ---
    if user_input_value:
        logger.info(f"User input received: {user_input_value}")

        # Send user input to agent
        if st.session_state.agent:
            follow_up_request = AgentInputSchema(
                topic="", # Maintain topic context
                target_language=AgentConfig.target_language,
                user_input=user_input_value,
            )
            logger.info(f"Running agent with follow-up request: {follow_up_request.model_dump()}")
            try:
                with st.spinner("Agent thinking..."):
                    response: UIOutputSchema = st.session_state.agent.run(follow_up_request)
                    st.session_state.current_response = response
                    logger.info(f"Agent follow-up response received: {response.model_dump(exclude={'image_s3', 'audio_s3'})}")
                    # Add agent response to messages
                    st.rerun()
            except Exception as e:
                logger.error(f"Error running agent follow-up: {e}", exc_info=True)
                st.error(f"Error running agent: {e}")
        else:
            st.error("Agent not initialized. Please generate an exercise first.")


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
