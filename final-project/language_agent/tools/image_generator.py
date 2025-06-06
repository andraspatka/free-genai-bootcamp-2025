import base64
from openai import OpenAI
import logging
import os
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ImageGeneratorToolInputSchema(BaseModel):
    """ 
    Schema for input to a tool for generating images using OpenAI's API.
    Takes a text string detailing the image to be generated.
    """
    description: str = Field(
        ..., 
        description="A text string detailing the image to be generated"
    )
    descriptive_filename: str = Field(
        ..., 
        description="A descriptive filename for the generated image. Should contain no whitespaces, words should be separated by underscore(_). File extension should be .png every time."
    )


class ImageGeneratorToolOutputSchema(BaseModel):
    """Output schema for the Image Generator tool."""
    image_base64: str = Field(..., description="Base64 encoded string of the generated image")
    filename: str = Field(..., description="The descriptive filename of the generated image")


class ImageGeneratorToolConfig(BaseModel):
    """Configuration for the Image Generator Tool."""
    openai_api_key: str = Field(..., description="API key for accessing OpenAI services")


class ImageGeneratorTool:
    """Tool for generating images using OpenAI's API.
    
    This tool takes a text description, generates an image using OpenAI's API,
    and returns the image as a base64 encoded string.
    
    Attributes:
        input_schema (ImageGeneratorToolInputSchema): The schema for the input data
        output_schema (ImageGeneratorToolOutputSchema): The schema for the output data
        config (ImageGeneratorToolConfig): Configuration containing OpenAI API key
    """
    input_schema = ImageGeneratorToolInputSchema
    output_schema = ImageGeneratorToolOutputSchema


    def __init__(self, config: ImageGeneratorToolConfig):
        """Initialize the ImageGeneratorTool with configuration."""
        self.config = config
        
        # Set OpenAI API key
        self.client = OpenAI(api_key=config.openai_api_key)


    def run(self, params: ImageGeneratorToolInputSchema) -> ImageGeneratorToolOutputSchema:
        """
        Run the image generation operation.
        
        Args:
            params (ImageGeneratorToolInputSchema): The input parameters containing the image description
            
        Returns:
            ImageGeneratorToolOutputSchema: The result of the image generation operation
            
        Raises:
            Exception: If there's an error during the image generation process
        """
        try:
            # Call OpenAI API to generate image
            response = self.client.images.generate(
                prompt=params.description,
                n=1,
                size="512x512",
                response_format="b64_json"
            )
            
            # Extract base64 image data
            image_base64 = response.data[0].b64_json
            
            return ImageGeneratorToolOutputSchema(
                image_base64=image_base64,
                filename=params.descriptive_filename
            )
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return ImageGeneratorToolOutputSchema(
                success=False,
                message=f"Error generating image: {str(e)}",
                image_base64=None
            )


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    # Initialize tool with config
    config = ImageGeneratorToolConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    image_generator = ImageGeneratorTool(config=config)
    
    # Create sample input
    input_params = ImageGeneratorToolInputSchema(
        description="A futuristic cityscape at sunset",
        descriptive_filename="futuristic_cityscape_at_sunset.png"
    )
    
    # Run the tool
    result = image_generator.run(input_params)
    print(result.model_dump_json(indent=2)[0:50])

    # Save the image to a file if generation was successful
    if result.image_base64:
        image_data = base64.b64decode(result.image_base64)
        with open(result.filename, "wb") as image_file:
            image_file.write(image_data)
        print(f"Image saved to {result.filename}")
