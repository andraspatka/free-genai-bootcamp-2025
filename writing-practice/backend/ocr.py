import cv2
import pytesseract
from PIL import Image
import boto3
import os


class OCRProcessor:
    def __init__(self):
        self.images_base_path = os.path.join('data', 'images')
        self.textract_client = boto3.client('textract', region_name="us-east-1")


    def preprocess_image(self, image_path: str) -> str:
        """Preprocess the image for better OCR results."""
        # Load the image
        img = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply binary thresholding
        _, binary = cv2.threshold(blurred, 0, 256, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Optionally apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Save the preprocessed image (optional)
        preprocessed_image_path = os.path.join(self.images_base_path, 'preprocessed_image.png')
        cv2.imwrite(preprocessed_image_path, morph)

        return preprocessed_image_path


    def tesseract_extract_text(self, image_path: str) -> str:
        """Extract text from the given image using Tesseract OCR."""
        preprocessed_image_path = self.preprocess_image(image_path)
        try:
            # Open the image file
            with Image.open(preprocessed_image_path) as img:
                # Use pytesseract to do OCR on the image
                text = pytesseract.image_to_string(img, lang='ita')  # Specify Italian language
            return text.strip()  # Return the extracted text
        except Exception as e:
            print(f"Error during OCR processing: {str(e)}")
        
            return ""

    def textract_extract_text(self, document_path: str) -> dict:
        """Extract text from the given document using Amazon Textract."""
        try:
            with open(document_path, 'rb') as document:
                response = self.textract_client.detect_document_text(Document={'Bytes': document.read()})
            
            # Extracting text blocks from the response
            extracted_text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    extracted_text += item['Text'] + "\n"
            return extracted_text.strip()
        except Exception as e:
            print(f"Error during Textract processing: {str(e)}")
            return ""




# Example usage
if __name__ == "__main__":
    ocr_processor = OCRProcessor()
    input_image = 'libro_pretty_handwritten.jpg'

    extracted_text = ocr_processor.tesseract_extract_text(f"data/images/{input_image}")
    print(f"Extracted Text using tesseract: {extracted_text}")
    extracted_text = ocr_processor.textract_extract_text(f"data/images/{input_image}")
    print(f"Extracted Text using textract: {extracted_text}")