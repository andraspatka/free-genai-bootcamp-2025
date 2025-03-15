import gradio as gr
import os
from backend.prompts import LanguagePrompts
from backend.lang_portal_client import LangPortalClient
from backend.ocr import OCRProcessor

# Initialize services
language_prompts = LanguagePrompts()
lang_portal_client = LangPortalClient("http://lang-portal-api:8000/api")
ocr_processor = OCRProcessor()


def generate_sentence(state):
    """Generate a sentence and store it in state"""
    word = lang_portal_client.get_random_word()
    response = language_prompts.generate_sentence(word)
    
    # Update state
    state.random_word = word
    state.english_sentence = response.get('sentence', '')
    
    return state, response.get('sentence', '')


def process_image(image_path, state):
    """Process uploaded image and perform OCR"""
    if image_path is None:
        return state, "No image uploaded"
    
    # Save the uploaded image
    save_dir = os.path.join("data", "images")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, os.path.basename(image_path))
    
    # Copy the uploaded image to our directory
    with open(save_path, "wb") as f:
        f.write(open(image_path, "rb").read())
    
    # Store image path in state
    state.image_path = save_path
    
    # Perform OCR
    extracted_text = ocr_processor.textract_extract_text(save_path)
    state.extracted_text = extracted_text
    
    # Grade the translation
    if state.english_sentence and extracted_text:
        grading_result = language_prompts.grade_translation(state.english_sentence, extracted_text)
        return state, f"Extracted text: {extracted_text}\n\nGrading: {grading_result.get('feedback', '')}\nScore: {grading_result.get('score', 0)}"
    
    return state, f"Extracted text: {extracted_text}"


# Gradio Interface
with gr.Blocks() as app:
    # Initialize session state
    state = gr.BrowserState([
        "",
        "",
        "",
        "",
    ])

    
    setup_button = gr.Button("Generate Sentence")
    sentence_output = gr.Textbox(label="English Sentence", interactive=False)
    
    setup_button.click(generate_sentence, inputs=[state], outputs=[state, sentence_output])

    # Display the current English sentence
    gr.Textbox(label="Current English Sentence", interactive=False, value=state.english_sentence)
    
    # Image upload component
    image_input = gr.Image(label="Upload your handwritten Italian translation", type="filepath", onchange=process_image)
    
    # Output display
    result_output = gr.Textbox(label="Results", interactive=False)
    
    # Handle image upload
    image_input.change(
        process_image,
        inputs=[image_input, state],
        outputs=[state, result_output]
    )

if __name__ == "__main__":
    app.launch()