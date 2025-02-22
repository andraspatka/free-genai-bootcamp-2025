import streamlit as st
import os
from utils.llm_connector import OllamaLLMConnector
from utils.vocab_generator import VocabGenerator

def display_words():
    # Display Generated Vocabulary
    if 'vocab_list' in st.session_state:
        st.subheader(f"Generated {st.session_state.word_group}")
        st.table(st.session_state.vocab_list)

def main():
    st.title("Language Vocabulary Generator")
    
    # Initialize LLM Connector and Vocab Generator
    llm_connector = OllamaLLMConnector(
        endpoint=os.environ['OLLAMA_SERVER_ENDPOINT'],
        model=os.environ['OLLAMA_MODEL']
    )
    vocab_generator = VocabGenerator(llm_connector)
    
    # Sidebar for configuration
    st.sidebar.header("Vocabulary Generation Settings")
    word_group = st.sidebar.selectbox(
        "Select Word Group", 
        ["Adjectives", "Verbs", "Nouns", "Adverbs"]
    )
    num_words = st.sidebar.slider("Number of Words", 5, 20, 10)
    language = st.sidebar.selectbox(
        "Target Language", 
        ["Italian"]
    )

    display_words()
    
    # Generate Vocabulary Button
    if st.sidebar.button("Generate Vocabulary"):
        with st.spinner(f"Generating {word_group.lower()}..."):
            vocab_list = vocab_generator.generate_vocab(
                word_group.lower(), 
                language, 
                num_words
            )
            st.session_state.vocab_list = vocab_list
            st.session_state.word_group = word_group
        
        display_words()
        
    if 'vocab_list' in st.session_state:
        # Export Options
        export_filename = f"{st.session_state.word_group.lower()}_{language.lower()}.json"
        export_path = os.path.join("exports", export_filename)
        if st.button(f"Export to {export_filename}"):
            print(f"Exporting to {export_path}")
            print(f"Vocabulary list: {st.session_state.vocab_list}")
            vocab_generator.export_to_json(st.session_state.vocab_list, export_path)
            st.success(f"Vocabulary exported to {export_path}")

if __name__ == "__main__":
    main()
