import streamlit as st
import logging

from backend.agent import LanguageExerciseAgent
from backend.schemas import AgentInputSchema, UserInteractionSchema, EvaluationSchema, FinalOutputSchema, AgentOutputSchema
from atomic_agents.schemas.chat_message import ChatMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Language Learning Exercise Generator", layout="wide")

st.title("💬 Language Learning Exercise Generator")
st.caption("🚀 An AI agent to create custom language exercises")

# Initialize Agent (consider caching for efficiency)
@st.cache_resource
def get_agent():
    logger.info("Initializing LanguageExerciseAgent for Streamlit session.")
    return LanguageExerciseAgent()

agent = get_agent()

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = [] # Stores ChatMessage history for the agent
if 'current_exercise_state' not in st.session_state:
    # Stores the agent's output (UserInteraction, Evaluation, or Final)
    st.session_state.current_exercise_state = None
if 'exercise_in_progress' not in st.session_state:
    st.session_state.exercise_in_progress = False
if 'last_interaction_prompt' not in st.session_state:
    st.session_state.last_interaction_prompt = None
if 'last_media_path' not in st.session_state:
     st.session_state.last_media_path = None

# --- Sidebar for New Exercise Configuration ---
st.sidebar.header("New Exercise Settings")
with st.sidebar.form("exercise_form", clear_on_submit=False):
    topic = st.text_input("Topic/Theme:", value="Greetings", help="E.g., 'Ordering food', 'Talking about hobbies'")
    difficulty = st.selectbox("Difficulty:", ["easy", "medium", "hard"], index=0)
    target_language = st.text_input("Target Language:", value="Italian")
    user_context = st.text_area("Optional User Context:", height=100, placeholder="E.g., beginner, needs practice with past tense")
    submitted = st.form_submit_button("Generate Exercise")

    if submitted and topic and difficulty and target_language:
        with st.spinner("Generating exercise..."):
            logger.info(f"New exercise request submitted: Topic={topic}, Difficulty={difficulty}, Lang={target_language}")
            st.session_state.messages = [] # Reset history for new exercise
            st.session_state.exercise_in_progress = True
            st.session_state.last_interaction_prompt = None
            st.session_state.last_media_path = None
            initial_input = AgentInputSchema(
                topic=topic,
                difficulty=difficulty,
                target_language=target_language,
                user_context=user_context or None
            )
            try:
                response = agent.run(input_data=initial_input)
                st.session_state.current_exercise_state = response
                # Add initial agent output to messages for display
                st.session_state.messages = agent.agent_system.memory.get_messages()
                logger.info(f"Initial agent response type: {type(response).__name__}")
                st.rerun() # Rerun to display the new state
            except Exception as e:
                logger.error(f"Error during initial agent run: {e}", exc_info=True)
                st.error(f"An error occurred: {e}")
                st.session_state.exercise_in_progress = False

# --- Main Chat/Exercise Display Area ---
col1, col2 = st.columns([2, 1]) # Main area and media area

with col1:
    st.subheader("Exercise Flow")
    # Display previous messages (excluding initial system prompt if desired)
    for msg in st.session_state.messages:
        if msg.role == "system": continue # Don't usually show system prompt
        with st.chat_message(msg.role):
            st.markdown(msg.content)
            # Display tool calls/responses if present
            if msg.tool_calls:
                with st.expander("Tool Calls"):
                     for tc in msg.tool_calls:
                         st.code(f"{tc.tool_name}({tc.arguments})", language="json")
            if msg.tool_call_responses:
                 with st.expander("Tool Responses"):
                    for tr in msg.tool_call_responses:
                         st.code(tr.content, language="json")

    # Display current state based on agent output
    current_state = st.session_state.current_exercise_state
    if current_state:
        with st.chat_message("assistant"):
            if isinstance(current_state, UserInteractionSchema):
                st.markdown(current_state.prompt_to_user)
                st.session_state.last_interaction_prompt = current_state.prompt_to_user
                st.session_state.last_media_path = current_state.media_s3_path
                # Input area handled below

            elif isinstance(current_state, EvaluationSchema):
                st.markdown("**Feedback:**")
                st.markdown(current_state.evaluation_feedback)
                if current_state.is_correct is not None:
                    st.markdown(f"**Correct:** {current_state.is_correct}")
                # Exercise might continue or end here based on agent logic
                # For simplicity, assume exercise ends after evaluation for now
                st.session_state.exercise_in_progress = False
                st.info("Exercise evaluation complete.")

            elif isinstance(current_state, FinalOutputSchema):
                st.markdown(f"**Exercise Complete: {current_state.exercise_type} ({current_state.difficulty})**")
                if current_state.text_content:
                    st.markdown("**Content:**")
                    st.markdown(current_state.text_content)
                if current_state.quiz_questions:
                    st.markdown("**Quiz:**")
                    for i, q in enumerate(current_state.quiz_questions):
                        st.markdown(f"{i+1}. {q.question}")
                        with st.expander("Show Answer"):
                            st.markdown(q.correct_answer)
                st.session_state.last_media_path = current_state.image_s3_path or current_state.audio_s3_path
                st.session_state.exercise_in_progress = False
                st.success("Exercise generated successfully!")
            else:
                # Handle unexpected state
                st.error("An unexpected state was reached.")
                st.code(str(current_state), language="text")
                st.session_state.exercise_in_progress = False

# --- Media Display Area ---
with col2:
    st.subheader("Media")
    media_path = st.session_state.last_media_path
    if media_path:
        st.markdown(f"*Media Path: `{media_path}`* ")
        # Naive check for image/audio based on common extensions or prefixes
        # WARNING: This is basic. A robust solution needs proper S3 integration/URL signing
        #          or direct fetching based on the path.
        #          For now, it assumes the S3 path might be a public URL or recognizable pattern.
        if media_path.startswith("s3://") or "://" not in media_path:
             st.warning(f"Cannot directly display S3 path: {media_path}. Need pre-signed URL or public access.")
             # TODO: Add logic here to generate pre-signed URL if possible
        elif any(ext in media_path.lower() for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]):
            st.image(media_path, caption="Exercise Image")
        elif any(ext in media_path.lower() for ext in [".mp3", ".wav", ".ogg", ".m4a"]):
            st.audio(media_path, format='audio/mpeg') # Adjust format if needed
        else:
            st.info("Media link provided, but type is undetermined for display.")
            st.markdown(f"[Link to Media]({media_path})")
    else:
        st.info("No media associated with the current step.")

# --- Chat Input Area ---
# Only show input if the agent asked a question (UserInteractionSchema)
if st.session_state.exercise_in_progress and isinstance(st.session_state.current_exercise_state, UserInteractionSchema):
    prompt = st.session_state.last_interaction_prompt or "Your response:"
    user_input = st.chat_input(prompt)

    if user_input:
        logger.info(f"User submitted input: {user_input[:100]}...")
        # Display user message immediately
        with col1:
             with st.chat_message("user"):
                st.markdown(user_input)

        # Send to agent
        with st.spinner("Agent is thinking..."):
            user_message = ChatMessage(role="user", content=user_input)
            st.session_state.messages.append(user_message) # Add user message to stored history
            try:
                # Pass the updated history to the agent
                response = agent.run(input_data=user_message, chat_history=st.session_state.messages)
                st.session_state.current_exercise_state = response
                # Update message history from agent's memory AFTER the run
                st.session_state.messages = agent.agent_system.memory.get_messages()
                logger.info(f"Agent response type after user input: {type(response).__name__}")
                st.rerun()
            except Exception as e:
                logger.error(f"Error during agent run after user input: {e}", exc_info=True)
                st.error(f"An error occurred: {e}")
                st.session_state.exercise_in_progress = False
elif not st.session_state.exercise_in_progress:
     st.info("Generate a new exercise using the sidebar settings or review the completed one.")

