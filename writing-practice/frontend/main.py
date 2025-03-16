import random
import gradio as gr
import os
from backend.prompts import LanguagePrompts
from backend.lang_portal_client import LangPortalClient
from backend.ocr import OCRProcessor

# Initialize services
language_prompts = LanguagePrompts()
lang_portal_client = LangPortalClient("http://lang-portal-api:8000/api")
ocr_processor = OCRProcessor()


def generate_sentence():
    """Generate a sentence and store it in state"""
    random_word = lang_portal_client.get_random_word()
    sentence = language_prompts.generate_sentence(random_word)
    
    return sentence, random_word


def process_image(image_path):
    """Process uploaded image and perform OCR"""
    ocr_processor.preprocess_image(image_path)
    return 'data/images/preprocessed_image.png'

def extract_text(image_path):
    """Extract text from the given image using Tesseract OCR"""
    return ocr_processor.tesseract_extract_text(image_path), ocr_processor.textract_extract_text(image_path)

def extract_without_preprocessing(image_path):
    """Extract text from the given image using Amazon Textract"""
    return ocr_processor.textract_extract_text(image_path)

def grade_translation(sentence_en, sentence_it):
    grading = language_prompts.grade_translation(sentence_en, sentence_it)
    feedback = grading['feedback']
    score = grading['score']
    is_correct = grading['is_correct']

    return f"""
Your translation is {"correct" if is_correct else "incorrect"}!
Final score: {score}
Feedback: {feedback}
"""


# Gradio Interface
with gr.Blocks() as app:

    setup_button = gr.Button("Generate Sentence")
    
    sentence_output = gr.Textbox(label="English Sentence", interactive=False)
    random_word = gr.Textbox(label="Random Word", interactive=False)

    setup_button.click(generate_sentence, outputs=[sentence_output, random_word])
    
    image_input = gr.Image(label="Upload your handwritten Italian translation", type="filepath")
    textract_output = gr.Textbox(label="Amazon Textract Output", interactive=False)

    feedback = gr.Textbox(label="Feedback", interactive=False)
    # Textract strangely works better without preprocessing!
    image_input.change(extract_without_preprocessing, inputs=[image_input], outputs=[textract_output])
    textract_output.change(grade_translation, inputs=[sentence_output, textract_output], outputs=[feedback])
    

if __name__ == "__main__":
    app.launch()