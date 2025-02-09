from pydantic import BaseModel, Field

class UploadImage(BaseModel):
    """
    Schema for uploading an image.
    
    Attributes:
        image_bytes (bytes): The binary data of the image.
        image_name (str): The name of the image file.
    """
    image_bytes: bytes = Field(..., description="The binary data of the image")
    image_name: str = Field(..., description="The name of the image file")
