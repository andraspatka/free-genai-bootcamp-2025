import os
import base64
import tempfile
import logging
from typing import Optional

import boto3
from pydantic import Field

from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

################
# INPUT SCHEMA #
################
class S3UploaderToolInputSchema(BaseIOSchema):
    """
    Schema for input to a tool for uploading files to S3.
    Takes a base64 encoded string and filename, decodes and uploads to S3.
    """
    base64_content: str = Field(
        ..., 
        description="The base64 encoded content of the file to upload"
    )
    filename: str = Field(
        ..., 
        description="The name of the file to be saved in S3"
    )
    content_type: Optional[str] = Field(
        None,
        description="The content type (MIME type) of the file. If not provided, will be guessed from the filename."
    )

####################
# OUTPUT SCHEMA(S) #
####################
class S3UploaderToolOutputSchema(BaseIOSchema):
    """Output schema for the S3 Uploader tool."""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Status message about the upload")
    s3_path: Optional[str] = Field(None, description="The full S3 path where the file was uploaded")

##############
# TOOL LOGIC #
##############
class S3UploaderToolConfig(BaseToolConfig):
    """Configuration for the S3 Uploader Tool."""
    bucket_name: str = Field(..., description="The name of the S3 bucket to upload to")
    aws_access_key_id: Optional[str] = Field(None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS secret access key")
    aws_region: str = Field("us-east-1", description="AWS region")

class S3UploaderTool(BaseTool):
    """
    Tool for uploading files to S3.
    
    This tool takes a base64 encoded string and filename, decodes the content,
    saves it temporarily to disk, and uploads it to the specified S3 bucket.
    
    Attributes:
        input_schema (S3UploaderToolInputSchema): The schema for the input data
        output_schema (S3UploaderToolOutputSchema): The schema for the output data
        config (S3UploaderToolConfig): Configuration containing S3 bucket and credentials
    """
    
    input_schema = S3UploaderToolInputSchema
    output_schema = S3UploaderToolOutputSchema

    def __init__(self, config: S3UploaderToolConfig):
        """Initialize the S3UploaderTool with configuration."""
        super().__init__(config)
        self.bucket_name = config.bucket_name
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_region
        )

    def _save_base64_to_file(self, base64_content: str, filename: str) -> str:
        """
        Decode base64 content and save to a temporary file.
        
        Args:
            base64_content (str): The base64 encoded content
            filename (str): The name of the file
            
        Returns:
            str: Path to the temporary file
            
        Raises:
            ValueError: If the base64 content is invalid
        """
        try:
            # Create a temporary directory that persists until explicitly deleted
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, filename)
            
            # Decode and write the content
            file_content = base64.b64decode(base64_content)
            with open(temp_file_path, 'wb') as f:
                f.write(file_content)
            
            return temp_file_path
        except Exception as e:
            logger.error(f"Error saving base64 content to file: {str(e)}")
            raise ValueError(f"Invalid base64 content: {str(e)}")

    def _guess_content_type(self, filename: str) -> str:
        """
        Guess the content type from the filename extension.
        
        Args:
            filename (str): The name of the file
            
        Returns:
            str: The guessed content type
        """
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'

    def run(self, params: S3UploaderToolInputSchema) -> S3UploaderToolOutputSchema:
        """
        Run the S3 upload operation.
        
        Args:
            params (S3UploaderToolInputSchema): The input parameters containing the file content and name
            
        Returns:
            S3UploaderToolOutputSchema: The result of the upload operation
            
        Raises:
            Exception: If there's an error during the upload process
        """
        try:
            # Save the base64 content to a temporary file
            temp_file_path = self._save_base64_to_file(
                params.base64_content,
                params.filename
            )
            
            # Determine content type
            content_type = params.content_type or self._guess_content_type(params.filename)
            
            try:
                # Upload to S3
                self.s3_client.upload_file(
                    temp_file_path,
                    self.bucket_name,
                    params.filename,
                    ExtraArgs={'ContentType': content_type}
                )
                
                # Construct the S3 path
                s3_path = f"s3://{self.bucket_name}/{params.filename}"
            finally:
                # Clean up: remove the temporary file and directory
                try:
                    os.unlink(temp_file_path)  # Delete the file
                    os.rmdir(os.path.dirname(temp_file_path))  # Delete the directory
                except Exception as e:
                    logger.warning(f"Error cleaning up temporary files: {e}")
            
            return S3UploaderToolOutputSchema(
                success=True,
                message=f"File successfully uploaded to {s3_path}",
                s3_path=s3_path
            )
            
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return S3UploaderToolOutputSchema(
                success=False,
                message=f"Error uploading to S3: {str(e)}",
                s3_path=None
            )


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    # Create sample base64 content
    sample_content = "Hello, World!"
    base64_content = base64.b64encode(sample_content.encode()).decode()

    # Initialize tool with config
    config = S3UploaderToolConfig(
        bucket_name=os.getenv("AWS_S3_BUCKET", ""),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    uploader = S3UploaderTool(config=config)

    # Create input
    upload_input = S3UploaderToolInputSchema(
        base64_content=base64_content,
        filename="test.txt",
        content_type="text/plain"
    )

    # Run the tool
    result = uploader.run(upload_input)
    print(result.model_dump_json(indent=2))