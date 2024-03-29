from typing import Dict, List, Optional
from pydantic import BaseModel


class ActiveResponseModel(BaseModel):
    """
    model that contains just a active attribute
    """
    active: bool


class DetailMessageResponseModel(BaseModel):
    """
    detail message as response
    """
    detail: str


class MessageResponseModel(BaseModel):
    """
    model that contains just a message attribute
    """
    message: str


class InstanceNotFoundErrorResponseModel(BaseModel):
    """
    format if instance not found in database
    """
    code: str = "INSTANCE_NOT_FOUND"
    message: str


class ValidationFailedResponseModel(BaseModel):
    """
    Model for Validation errors as defined in `app.validation_exception_handler`
    """
    detail: List
    body: Optional[Dict]


class PingResponseModel(BaseModel):
    """
    Response model
    """
    success: bool
    rtt_avg: str
    rtt_avg_ms: str
    rtt_max: str
    rtt_max_ms: str
    rtt_min: str
    rtt_min_ms: str


class UrlRequestModel(BaseModel):
    """
    request model for HTTP lookups
    """
    url: str
    ssl_verify: bool


class UrlResponseModel(BaseModel):
    """
    response model for HTTP lookups
    """
    content: str
    status: int
