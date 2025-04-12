import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def base64_to_pil_image(base64_str):
    """
    Convert a base64 encoded image string to a Pillow Image object.
    
    Args:
        base64_str (str): Base64 encoded image string. Can include header like
                         'data:image/jpeg;base64,' which will be stripped.
                         
    Returns:
        PIL.Image.Image: Pillow Image object
    """
    try:
        # Strip header if present (e.g., "data:image/jpeg;base64,")
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
        
        # Decode base64 string to bytes
        img_bytes = base64.b64decode(base64_str)
        
        # Create Image object from bytes
        img = Image.open(BytesIO(img_bytes))
        
        return img
    except Exception as e:
        logger.error(f"Error converting base64 to PIL image: {e}")
        return None


def base64_to_audio(base64_str):
    """
    Convert a base64 encoded audio string to binary data for use with st.audio.
    
    Args:
        base64_str (str): Base64 encoded audio string
                         
    Returns:
        bytes: Binary audio data
    """
    try:
        # Strip header if present (e.g., "data:audio/mp3;base64,")
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
        
        # Decode base64 string to bytes
        audio_bytes = base64.b64decode(base64_str)
        
        return audio_bytes
    except Exception as e:
        logger.error(f"Error converting base64 to audio: {e}")
        return None

