import base64
import boto3
import logging
import os
import tempfile
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AudioGeneratorToolInputSchema(BaseModel):
    """ 
    Schema for input to a tool for generating audio using AWS Polly.
    Takes a text string to be converted to speech.
    """
    text: str = Field(
        ..., 
        description="The text to be converted to speech"
    )
    voice_id: Optional[Literal["Bianca"]] = Field(
        "Bianca", description="The voice ID to use for speech synthesis. Default is 'Bianca' (Italian female)"
    )
    descriptive_filename: str = Field(
        ..., 
        description="A descriptive filename for the generated audio. Should contain no whitespaces, words should be separated by underscore(_). File extension should be .mp3 every time."
    )
    language_code: str = Field(
        "it-IT",
        description="The language code for the voice. Default is 'it-IT' for Italian"
    )
    engine: Optional[Literal["generative"]] = Field(
        "generative",
        description="The engine to use for speech synthesis. Options is 'generative'"
    )


class AudioGeneratorToolOutputSchema(BaseModel):
    """Output schema for the Audio Generator tool."""
    audio_base64: str = Field(..., description="Base64 encoded string of the generated audio")
    filename: str = Field(..., description="The descriptive filename of the generated audio")
    success: bool = Field(True, description="Whether the audio generation was successful")
    message: Optional[str] = Field(None, description="Error message if generation failed")


class AudioGeneratorToolConfig(BaseModel):
    """Configuration for the Audio Generator Tool."""
    aws_access_key_id: str = Field(..., description="AWS access key ID")
    aws_secret_access_key: str = Field(..., description="AWS secret access key")
    aws_region: str = Field("us-east-1", description="AWS region")


class AudioGeneratorTool:
    """Tool for generating audio using AWS Polly.
    
    This tool takes a text description, generates audio using AWS Polly,
    and returns the audio as a base64 encoded string.
    
    Attributes:
        input_schema (AudioGeneratorToolInputSchema): The schema for the input data
        output_schema (AudioGeneratorToolOutputSchema): The schema for the output data
        config (AudioGeneratorToolConfig): Configuration containing AWS credentials
    """
    input_schema = AudioGeneratorToolInputSchema
    output_schema = AudioGeneratorToolOutputSchema

    # Available Italian voices in AWS Polly
    ITALIAN_VOICES = {
        'male': ['Giorgio'],
        'female': ['Carla', 'Bianca']
    }

    def __init__(self, config: AudioGeneratorToolConfig):
        """Initialize the AudioGeneratorTool with configuration."""
        self.config = config
        
        # Initialize AWS Polly client
        self.polly = boto3.client(
            'polly', 
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key
        )


    def run(self, params: AudioGeneratorToolInputSchema) -> AudioGeneratorToolOutputSchema:
        """
        Run the audio generation operation.
        
        Args:
            params (AudioGeneratorToolInputSchema): The input parameters containing the text to convert to speech
            
        Returns:
            AudioGeneratorToolOutputSchema: The result of the audio generation operation
            
        Raises:
            Exception: If there's an error during the audio generation process
        """
        try:
            voice_id = params.voice_id
            
            # Call AWS Polly to generate speech
            response = self.polly.synthesize_speech(
                Text=params.text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=params.engine,
                LanguageCode=params.language_code
            )
            
            # Create a temporary file to store the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                # Write audio data to the temporary file
                audio_data = response['AudioStream'].read()
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
                # Read the audio file and encode it in base64
                with open(temp_file_path, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            return AudioGeneratorToolOutputSchema(
                audio_base64=audio_base64,
                filename=params.descriptive_filename,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return AudioGeneratorToolOutputSchema(
                audio_base64="",
                filename=params.descriptive_filename,
                success=False,
                message=f"Error generating audio: {str(e)}"
            )


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    # Initialize tool with config
    config = AudioGeneratorToolConfig(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.getenv("AWS_REGION")
    )
    
    audio_generator = AudioGeneratorTool(config=config)
    
    # Create sample input
    input_params = AudioGeneratorToolInputSchema(
        text="Ciao, come stai oggi? Spero che tu stia bene!",
        voice_id="Bianca",
        descriptive_filename="italian_greeting.mp3",
        language_code="it-IT",
        engine="generative"
    )
    
    # Run the tool
    result = audio_generator.run(input_params)
    print(f"Success: {result.success}")
    if not result.success:
        print(f"Error: {result.message}")
    else:
        print(f"Audio base64 (first 50 chars): {result.audio_base64[:50]}...")

    # Save the audio to a file if generation was successful
    if result.success and result.audio_base64:
        audio_data = base64.b64decode(result.audio_base64)
        with open(result.filename, "wb") as audio_file:
            audio_file.write(audio_data)
        print(f"Audio saved to {result.filename}")
