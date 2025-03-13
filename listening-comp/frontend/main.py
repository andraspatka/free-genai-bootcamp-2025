import streamlit as st
from typing import Dict
import json
from collections import Counter
import re
from datetime import datetime

import os


from backend.chat import BedrockChat
from backend.get_transcript import YouTubeTranscriptDownloader
from backend.structured_data import TranscriptStructurer
from backend.rag import ExerciseVectorStore, ExerciseGenerator
from backend.audio_generator import AudioGenerator
from backend.interactive import ListeningComprehension


# Page config
st.set_page_config(
    page_title="Italian Learning Assistant",
    page_icon="🇮🇹",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'transcript_structure' not in st.session_state:
    st.session_state.transcript_structure = ""

def render_header():
    """Render the header section"""
    st.title("🇮🇹 Italian Learning Assistant")
    st.markdown("""
    Transform YouTube transcripts into interactive Italian learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Amazon Bedrock Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.header("Development Stages")
        
        # Main component selection
        selected_stage = st.radio(
            "Select Stage:",
            [
                "1. Chat with Nova",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Stage descriptions
        stage_info = {
            "1. Chat with Nova": """
            **Current Focus:**
            - Basic Italian learning
            - Understanding LLM capabilities
            - Identifying limitations
            """,
            
            "2. Raw Transcript": """
            **Current Focus:**
            - YouTube transcript download
            - Raw text visualization
            - Initial data examination
            """,
            
            "3. Structured Data": """
            **Current Focus:**
            - Text cleaning
            - Dialogue extraction
            - Data structuring
            """,
            
            "4. RAG Implementation": """
            **Current Focus:**
            - Bedrock embeddings
            - Vector storage
            - Context retrieval
            """,
            
            "5. Interactive Learning": """
            **Current Focus:**
            - Scenario generation
            - Audio synthesis
            - Interactive practice
            """
        }
        
        st.markdown("---")
        st.markdown(stage_info[selected_stage])
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with Nova")

    # Initialize BedrockChat instance if not in session state
    if 'bedrock_chat' not in st.session_state:
        st.session_state.bedrock_chat = BedrockChat()

    # Introduction text
    st.markdown("""
    Start by exploring Nova's base Italian language capabilities. Try asking questions about Italian grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about Italian language..."):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in Italian?",
            "How do I count objects in Italian?",
            "How do I ask for directions politely in Italian?"
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary"):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages = []
            st.session_state.bedrock_chat.clear_messages()
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        response = st.session_state.bedrock_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})



def count_characters(text):
    """Count Italian and total characters in text"""
    if not text:
        return 0, 0
        
    def is_Italian(char):
        return any([
            '\u4e00' <= char <= '\u9fff',  # Kanji
            '\u3040' <= char <= '\u309f',  # Hiragana
            '\u30a0' <= char <= '\u30ff',  # Katakana
        ])
    
    jp_chars = sum(1 for char in text if is_Italian(char))
    return jp_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a Italian lesson YouTube URL"
    )

    if 'youtube_transcript_downloader' not in st.session_state:
        st.session_state.youtube_transcript_downloader = YouTubeTranscriptDownloader()
    if 'video_id' not in st.session_state:
        st.session_state.video_id = ""

    # st.write(st.session_state.transcript)
    # Download button and processing
    if url:
        os.write(1, b'URL true')
        if st.button("Download Transcript"):
            try:
                transcript = st.session_state.youtube_transcript_downloader.get_transcript(url)
                st.session_state.video_id = st.session_state.youtube_transcript_downloader.extract_video_id(url)
                st.session_state.youtube_transcript_downloader.save_transcript(transcript, st.session_state.video_id)
                if transcript:
                    # Store the raw transcript text in session state
                    transcript_text = "\n".join([entry['text'] for entry in transcript])
                    st.session_state.transcript = transcript_text
                    st.success("Transcript downloaded successfully!")
                else:
                    st.error("No transcript found for this video.")
            except Exception as e:
                st.error(f"Error downloading transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            jp_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars)
            st.metric("Italian Characters", jp_chars)
            st.metric("Total Lines", total_lines)
        else:
            st.info("Load a transcript to see statistics")


def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    col1, col2 = st.columns(2)

    if 'transcript_structurer' not in st.session_state:
        st.session_state.transcript_structurer = TranscriptStructurer()
    
    
    with col1:
        st.subheader("Dialogue Extraction")
        # Placeholder for dialogue processing
        # st.write(st.session_state.transcript)
        if st.session_state.transcript:
            st.text_area(
                label="transcript",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
            if st.button("Structure transcript"):
                transcript_structure = st.session_state.transcript_structurer.structure_transcript(st.session_state.transcript)
                st.session_state.transcript_structure = transcript_structure
                st.session_state.transcript_structurer.save_to_file(transcript_structure, st.session_state.video_id)

                if st.button("Add to Vector DB"):
                    st.session_state.vector_db.add_document(transcript_structure)
        else:
            st.info("Load a transcript to start")
        
    with col2:
        st.subheader("Data Structure")
        # Placeholder for structured data view
        if st.session_state.transcript_structure:
            st.text_area(
                label="structured data",
                value=st.session_state.transcript_structure,
                height=400,
                disabled=True
            )
        else:
            st.info("Load a transcript to see the structured data")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")

    if 'exercise_vector_store' not in st.session_state:
        st.session_state.exercise_vector_store = ExerciseVectorStore()
        st.session_state.exercise_vector_store.load_data()
    if 'exercise_generator' not in st.session_state:
        st.session_state.exercise_generator = ExerciseGenerator()


    # Query input
    placeholder = "Enter a situation that you would like to practice / A scenario to generate"
    query = st.text_input(
        "Test Query",
        placeholder=placeholder
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retrieved Context")
        if st.button("Search vector store"):
            exercise = st.session_state.exercise_vector_store.search_similar_exercises(query, n_results=1)[0]
            st.text_area(
                label="Raw text",
                value=exercise,
                height=400,
                disabled=True
            )
        
    with col2:
        st.subheader("Generated Response")
        if st.button("Generate new exercise"):
            exercise = st.session_state.exercise_generator.generate_similar_exercise(query)
            st.text_area(
                label="Raw text",
                value=exercise,
                height=400,
                disabled=True
            )

def render_interactive_stage():
    """Render the interactive learning stage"""
    st.header("Interactive Learning")
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        ["Listening Exercise"]
    )

    if 'audio_generator' not in st.session_state:
        st.session_state.audio_generator = AudioGenerator()
    if 'listening_comprehension' not in st.session_state:
        st.session_state.listening_comprehension = ListeningComprehension()
    if 'audio_file_path' not in st.session_state:
        st.session_state.audio_file_path = None
    if 'interactive_exercise_data' not in st.session_state:
        st.session_state.interactive_exercise_data = None
    if 'interactive_exercise_video_data' not in st.session_state:
        st.session_state.interactive_exercise_video_data = None
    if 'interactive_exercise_questions' not in st.session_state:
        st.session_state.interactive_exercise_questions = None
    if 'interactive_exercise_selected' not in st.session_state:
        st.session_state.interactive_exercise_selected = None
    
    st.subheader("Audio")
    # Placeholder for audio player
    if st.button("Get Listening Exercise"):
        st.session_state.interactive_exercise_data, st.session_state.interactive_exercise_video_id = \
            st.session_state.listening_comprehension.get_text()
        st.session_state.audio_file_path = st.session_state.audio_generator.generate_audio(
            st.session_state.interactive_exercise_data["transcript"],
            voice_name="Carla",
            video_id=st.session_state.interactive_exercise_video_id
        )
        st.audio(st.session_state.audio_file_path)
        st.session_state.interactive_exercise_questions = st.session_state.listening_comprehension.generate_questions(
            st.session_state.interactive_exercise_data["transcript"]
        )


    st.subheader("Practice Scenario")
    # Placeholder for scenario
    st.text_area(
        label="Raw text - only for debugging purposes",
        value=st.session_state.interactive_exercise_data,
        height=400,
        disabled=True
    )
    
    if st.session_state.interactive_exercise_questions:
        st.text(st.session_state.interactive_exercise_questions["questions"][0]["question"])
        options = [q["option"] for q in st.session_state.interactive_exercise_questions["questions"][0]["options"]]
        selected = st.radio("Choose your answer:", options, key="interactive_exercise_question")
        st.session_state.interactive_exercise_selected = selected

    if st.button("Check"):
        st.subheader("Feedback")
        if st.session_state.interactive_exercise_selected:
            choice = [
                q["number"]
                for q in st.session_state.interactive_exercise_questions["questions"][0]["options"] 
                if q["option"] == st.session_state.interactive_exercise_selected
            ][0]
            feedback = [
                q["feedback"]
                for q in st.session_state.interactive_exercise_questions["questions"][0]["options"] 
                if q["option"] == st.session_state.interactive_exercise_selected
            ][0]
            correct_answer = st.session_state.interactive_exercise_questions["questions"][0]["correct_answer"]
            is_correct = choice == correct_answer
            st.text_area(
                label="Feedback",
                value=f"""
                    Your choice is {is_correct}
                    Feedback: {feedback}
                """,
                height=400,
                disabled=True
            )


def main():
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with Nova":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        render_interactive_stage()
    
    # Debug section at the bottom
    with st.expander("Debug Information"):
        st.json({
            "selected_stage": selected_stage,
            "transcript_loaded": st.session_state.transcript != "",
            "chat_messages": len(st.session_state.messages)
        })

if __name__ == "__main__":
    main()