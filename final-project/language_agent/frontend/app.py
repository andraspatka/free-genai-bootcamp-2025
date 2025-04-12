import streamlit as st
import logging

import os

from language_agent.backend.agent import LanguageExerciseAgent
from language_agent.backend.schemas import AgentInputSchema, UIOutputSchema, QuizSchema, QuizOptionSchema
from language_agent.backend.config import AgentConfig # For default language
from language_agent.frontend.session_state import initialize_session_state
from language_agent.frontend.ui_components import display_quiz, header, footer, render_chat_messages

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

if os.getenv("DEBUG"):
    if 'debug' not in st.session_state:
        st.session_state.debug = True
        debug()

# --- Initialize Session State --- Must be called early
initialize_session_state()

def main():
    # --- UI Layout ---
    st.set_page_config(layout="wide", page_title="LinguaLearn AI")
    st.title("🇮🇹 LinguaLearn AI Tutor 🇮🇹")

    # --- Header Panel ---
    header()

    # --- Main Content Area ---
    if st.session_state.exercise_started and st.session_state.current_response:
        st.divider()
        difficulty = st.session_state.difficulty
        logger.info(f"Displaying content for difficulty: {difficulty}")

        # --- Chat Input (Common) ---
        # Place chat input outside the columns to ensure it's always visible when exercise is active
        user_input_value = st.chat_input("Your response:", key=f"chat_input_{st.session_state.input_key}")

        # --- Populate Placeholders based on difficulty ---
        if difficulty == "easy":
            st.subheader("Conversation")
            render_chat_messages()

        elif difficulty in ["medium", "hard"]:
            col_chat, col_resources = chat_placeholder.columns(2)

            with col_chat:
                st.subheader("Conversation")
                render_chat_messages()

            with col_resources:
                st.subheader("Resources")
                latest_response = st.session_state.current_response
                # Find the first message with the resource if latest doesn't have it (e.g., image only shown once)
                initial_image_msg = next((msg for msg in st.session_state.messages if msg["role"] == "assistant" and msg.get("image_s3")), None)
                initial_audio_msg = next((msg for msg in st.session_state.messages if msg["role"] == "assistant" and msg.get("audio_s3")), None)
                initial_quiz_msg = next((msg for msg in st.session_state.messages if msg["role"] == "assistant" and msg.get("quiz")), None)


                if difficulty == "medium":
                    image_s3_to_display = latest_response.image_s3 if hasattr(latest_response, 'image_s3') and latest_response.image_s3 else (initial_image_msg['image_s3'] if initial_image_msg else None)
                    if image_s3_to_display:
                        st.image(image_s3_to_display, caption="🖼️ Generated Image", use_column_width=True)
                        logger.info(f"Displaying image from: {image_s3_to_display}")
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
            # Add user message to chat history IMMEDIATELY for better UX
            st.session_state.messages.append({"role": "user", "content": user_input_value})

            # Send user input to agent
            if st.session_state.agent:
                follow_up_request = AgentInputSchema(
                    topic=st.session_state.topic, # Maintain topic context
                    target_language=AgentConfig.target_language,
                    user_input=user_input_value
                )
                logger.info(f"Running agent with follow-up request: {follow_up_request.model_dump()}")
                try:
                    with st.spinner("Agent thinking..."):
                        response: UIOutputSchema = st.session_state.agent.run(follow_up_request)
                        st.session_state.current_response = response
                        logger.info(f"Agent follow-up response received: {response.model_dump(exclude={'image_s3', 'audio_s3'})}")
                        # Add agent response to messages
                    st.session_state.input_key += 1 # Increment key to clear input field
                    st.rerun() # Update UI with new messages and potentially updated resources
                except Exception as e:
                    logger.error(f"Error running agent follow-up: {e}", exc_info=True)
                    st.error(f"Error running agent: {e}")
            else:
                st.error("Agent not initialized. Please generate an exercise first.")
    elif st.session_state.exercise_started and not st.session_state.current_response:
        st.info("Generating initial exercise...") # Handles the case where the first run is in progress
    else:
        st.info("Select difficulty and enter a topic to start generating an exercise.")

    # --- Footer/Reset Button ---
    footer()

if __name__ == "__main__":
    main()