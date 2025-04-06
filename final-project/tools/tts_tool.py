from .schemas import TTSInputSchema, TTSOutputSchema
from .s3_tool import upload_to_s3 # Assuming s3_tool handles upload
import boto3
import os
from dotenv import load_dotenv
import logging
import uuid
from contextlib import closing

logger = logging.getLogger(__name__)
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not AWS_REGION or not S3_BUCKET_NAME:
    logger.warning("AWS_REGION or S3_BUCKET_NAME not configured. TTS tool may not fully function.")
    # Allow execution for local testing without AWS, maybe return dummy data

def generate_speech(input_data: TTSInputSchema) -> TTSOutputSchema:
    """Generates speech using Amazon Polly and uploads it to S3."""
    logger.info(f"Generating speech for text starting with: {input_data.text_to_speak[:50]}...")

    if not AWS_REGION or not S3_BUCKET_NAME:
         logger.error("AWS credentials or S3 bucket not configured.")
         # Return an error state or a dummy path
         return TTSOutputSchema(s3_path="error/not_configured.mp3", text_spoken=input_data.text_to_speak)

    try:
        # Initialize Polly client
        polly_client = boto3.Session(
            region_name=AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        ).client('polly')

        # --- Select Voice (Example: Italian Female) ---
        # Find available voices: aws polly describe-voices --language-code it-IT
        # Example voices: Aditi (Indian Female), Amy (British Female), Astrid (Swedish Female), Bianca (Italian Female), Brian (British Male)
        # Let's choose Bianca for Italian
        voice_id = 'Bianca'
        language_code = 'it-IT' # Adjust based on target language if dynamic

        response = polly_client.synthesize_speech(
            VoiceId=voice_id,
            OutputFormat='mp3',
            Text=input_data.text_to_speak,
            LanguageCode=language_code,
            Engine='neural' # Use neural engine for higher quality if available
        )

        if "AudioStream" in response:
            audio_data = None
            # Use closing to ensure the stream is closed
            with closing(response['AudioStream']) as stream:
                audio_data = stream.read()

            if audio_data:
                # Generate a unique filename
                file_extension = "mp3"
                unique_id = uuid.uuid4()
                s3_key = f"{input_data.s3_path_prefix}/{input_data.output_filename_prefix}_{unique_id}.{file_extension}"

                logger.info(f"Uploading generated audio to S3: {s3_key}")
                upload_response = upload_to_s3(
                    file_content=audio_data,
                    s3_key=s3_key,
                    content_type='audio/mpeg'
                )

                if upload_response.s3_path:
                     logger.info(f"Successfully generated and uploaded audio to {upload_response.s3_path}")
                     return TTSOutputSchema(
                         s3_path=upload_response.s3_path,
                         text_spoken=input_data.text_to_speak
                    )
                else:
                    logger.error("Failed to upload generated audio to S3.")
                    # Return error state
                    return TTSOutputSchema(s3_path=f"error/upload_failed.mp3", text_spoken=input_data.text_to_speak)
            else:
                logger.error("Polly returned an empty audio stream.")
                return TTSOutputSchema(s3_path=f"error/empty_stream.mp3", text_spoken=input_data.text_to_speak)
        else:
            logger.error("Polly API did not return an AudioStream.")
            return TTSOutputSchema(s3_path=f"error/no_stream.mp3", text_spoken=input_data.text_to_speak)

    except Exception as e:
        logger.error(f"Error during Text-to-Speech generation: {e}", exc_info=True)
        # Return error state
        return TTSOutputSchema(s3_path=f"error/exception_{type(e).__name__}.mp3", text_spoken=input_data.text_to_speak)

# Example usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Ensure AWS creds and S3 bucket are in .env or environment variables
    test_input = TTSInputSchema(
        text_to_speak="Ciao, come stai? Spero che tu stia imparando molto.",
        output_filename_prefix="test_italian_greeting",
        s3_path_prefix="test_audio"
    )
    output = generate_speech(test_input)
    print(output.model_dump_json(indent=2))
