import streamlit as st
import logging
from language_agent.frontend.session_state import initialize_session_state
from language_agent.frontend.ui_components import header, footer, main_content

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

    # --- Main Content ---
    main_content()

    # --- Footer/Reset Button ---
    footer()

if __name__ == "__main__":
    main()