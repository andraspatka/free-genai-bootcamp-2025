import os
import boto3
import logging
import tempfile
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

####################
# INPUT SCHEMA(S)  #
####################
class S3DownloaderToolInputSchema(BaseModel):
    """Schema for input to a tool for downloading files from S3.
    Takes an S3 path and downloads the file to a local directory.
    """
    s3_path: str = Field(
        ..., 
        description="The S3 path of the file to download (format: s3://bucket-name/path/to/file)"
    )
    local_directory: Optional[str] = Field(
        None,
        description="Optional local directory to save the file. If not provided, a temporary directory will be used."
    )

####################
# OUTPUT SCHEMA(S) #
####################
class S3DownloaderToolOutputSchema(BaseModel):
    """Output schema for the S3 Downloader tool."""
    success: bool = Field(..., description="Whether the download was successful")
    message: str = Field(..., description="Status message about the download")
    local_path: Optional[str] = Field(None, description="The full local path where the file was downloaded")

##############
# TOOL LOGIC #
##############
class S3DownloaderToolConfig(BaseModel):
    """Configuration for the S3 Downloader Tool."""
    aws_access_key_id: Optional[str] = Field(None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS secret access key")
    aws_region: str = Field("us-east-1", description="AWS region")

class S3DownloaderTool:
    """Tool for downloading files from S3.
    
    This tool takes an S3 path, downloads the content, and saves it to
    either a specified local directory or a temporary directory.
    
    Attributes:
        input_schema (S3DownloaderToolInputSchema): The schema for the input data
        output_schema (S3DownloaderToolOutputSchema): The schema for the output data
        config (S3DownloaderToolConfig): Configuration containing AWS credentials
    """
    input_schema = S3DownloaderToolInputSchema
    output_schema = S3DownloaderToolOutputSchema

    def __init__(self, config: S3DownloaderToolConfig):
        """Initialize the S3DownloaderTool with configuration."""
        self.config = config
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_region
        )

    def _parse_s3_path(self, s3_path: str) -> tuple[str, str]:
        """
        Parse an S3 path into bucket name and object key.
        
        Args:
            s3_path (str): The S3 path in format s3://bucket-name/path/to/file
            
        Returns:
            tuple[str, str]: Tuple of (bucket_name, object_key)
            
        Raises:
            ValueError: If the S3 path is invalid
        """
        if not s3_path.startswith('s3://'):
            raise ValueError("S3 path must start with 's3://'")
        
        path_without_prefix = s3_path[5:]  # Remove 's3://'
        parts = path_without_prefix.split('/', 1)
        
        if len(parts) != 2:
            raise ValueError("Invalid S3 path format. Expected: s3://bucket-name/path/to/file")
        
        bucket_name, object_key = parts
        return bucket_name, object_key

    def run(self, params: S3DownloaderToolInputSchema) -> S3DownloaderToolOutputSchema:
        """
        Run the S3 download operation.
        
        Args:
            params (S3DownloaderToolInputSchema): The input parameters containing the S3 path
            
        Returns:
            S3DownloaderToolOutputSchema: The result of the download operation
            
        Raises:
            Exception: If there's an error during the download process
        """
        try:
            # Parse S3 path
            bucket_name, object_key = self._parse_s3_path(params.s3_path)
            
            # Get filename from object key
            filename = os.path.basename(object_key)
            
            # Determine local directory
            if params.local_directory:
                local_dir = params.local_directory
                os.makedirs(local_dir, exist_ok=True)
            else:
                local_dir = tempfile.mkdtemp()
            
            # Construct local file path
            local_path = os.path.join(local_dir, filename)
            
            # Download the file
            self.s3_client.download_file(
                bucket_name,
                object_key,
                local_path
            )
            
            return S3DownloaderToolOutputSchema(
                success=True,
                message=f"File successfully downloaded to {local_path}",
                local_path=local_path
            )
            
        except Exception as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return S3DownloaderToolOutputSchema(
                success=False,
                message=f"Error downloading from S3: {str(e)}",
                local_path=None
            )


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    # Initialize tool with config
    config = S3DownloaderToolConfig(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.getenv("AWS_REGION")
    )

    bucket=os.getenv("S3_BUCKET_NAME", "")
    
    downloader = S3DownloaderTool(config=config)
    
    # Create sample input
    upload_input = S3DownloaderToolInputSchema(
        s3_path=f"s3://{bucket}/test.txt"
    )
    
    # Run the tool
    result = downloader.run(upload_input)
    print(result.model_dump_json(indent=2))
