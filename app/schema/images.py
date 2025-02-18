"""Pydantic schema for handling image uploads."""

from pydantic import BaseModel
from pydantic import Field


class UploadImage(BaseModel):
    """Schema for uploading an image.

    Attributes:
        image_bytes (bytes): The binary data of the image (must not be empty).
        image_name (str): The name of the image file (must not be empty).
    """

    image_bytes: bytes = Field(
        ...,
        min_length=1,
        description="Binary data of the image (cannot be empty).",
    )
    image_name: str = Field(
        ...,
        min_length=1,
        description="The name of the image file (cannot be empty).",
    )
