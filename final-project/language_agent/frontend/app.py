import streamlit as st
import logging

import os

from language_agent.backend.agent import LanguageExerciseAgent
from language_agent.backend.schemas import AgentInputSchema, UIOutputSchema, QuizSchema, QuizOptionSchema
from language_agent.backend.config import AgentConfig # For default language
from language_agent.frontend.session_state import initialize_session_state
from language_agent.frontend.ui_components import display_quiz, header, footer, render_chat_messages
from language_agent.frontend.util import base64_to_pil_image

from language_agent.tools import S3DownloaderTool, S3DownloaderToolConfig, S3DownloaderToolInputSchema

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug():
    import debugpy

    # Enable debugger
    debugpy.listen(("0.0.0.0", 5678))
    logger.info("⏳ Waiting for debugger to attach at 0.0.0.0:5678...")
    debugpy.wait_for_client()
    logger.info("🔍 Debugger attached! Starting application...")

# if os.getenv("DEBUG"):
#     if 'debug' not in st.session_state:
#         st.session_state.debug = True
#         debug()

# --- Initialize Session State --- Must be called early
initialize_session_state()

def main():
    # --- UI Layout ---
    st.set_page_config(layout="wide", page_title="LinguaLearn AI")
    st.title("🇮🇹 LinguaLearn AI Tutor 🇮🇹")

    # --- Header Panel ---
    header()

    chat = st.container()
    logging.info(st.session_state)

    # --- Main Content Area ---
    st.divider()
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

        with col_resources:
            st.subheader("Resources")
            latest_response = st.session_state.current_response
            if difficulty == "medium":
                if st.session_state.image is None:
                    s3_path = latest_response.image_s3

                    s3_dl_tool = S3DownloaderTool(
                        S3DownloaderToolConfig(
                            aws_access_key_id=AgentConfig.aws_access_key_id,
                            aws_secret_access_key=AgentConfig.aws_secret_access_key,
                            aws_region=AgentConfig.aws_region
                        )
                    )

                    image_base64 = s3_dl_tool.run(S3DownloaderToolInputSchema(s3_path=s3_path)).image_base64
                    st.session_state.image = base64_to_pil_image(image_base64)
                
                if st.session_state.image:
                    st.image(st.session_state.image, caption="🖼️ Generated Image", use_column_width=True)
                    logger.info(f"Displaying image from: ")
                else:
                    st.info("No image available for this exercise.")

            elif difficulty == "hard":
                st.info("Hard difficulty resources (Audio/Quiz) display area.")
                # Display Audio
                audio_s3_to_display = latest_response.audio_s3 if hasattr(latest_response, 'audio_s3') and latest_response.audio_s3 else (initial_audio_msg['audio_s3'] if initial_audio_msg else None)
                if audio_s3_to_display:
                    st.audio(audio_s3_to_display)
                    logger.info(f"Displaying audio from: {audio_s3_to_display}")

                # Display Quiz
                quiz_to_display = latest_response.quiz_questions if hasattr(latest_response, 'quiz_questions') and latest_response.quiz_questions else (initial_quiz_msg['quiz'] if initial_quiz_msg else None)
                if quiz_to_display:
                    logger.info("Displaying quiz.")
                    display_quiz(quiz_to_display)
                elif not audio_s3_to_display: # Only show 'no resources' if neither audio nor quiz is present
                    st.info("No audio or quiz available for this exercise.")


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

    # --- Footer/Reset Button ---
    footer()

if __name__ == "__main__":
    main()