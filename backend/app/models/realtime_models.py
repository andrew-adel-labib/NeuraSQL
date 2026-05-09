from typing import Optional

from pydantic import BaseModel


class TranscriptEvent(BaseModel):

    type: str = "transcript"

    text: str

    provider: Optional[str] = "claude"


class PartialTranscriptEvent(BaseModel):

    type: str = "partial_transcript"

    text: str


class FinalTranscriptEvent(BaseModel):

    type: str = "final_transcript"

    text: str


class AIResponseEvent(BaseModel):

    type: str = "ai_response"

    question: str

    provider: str

    sql: Optional[str] = None

    summary: str

    rows: list = []

    columns: list = []


class ErrorEvent(BaseModel):

    type: str = "error"

    message: str


class WebsocketStatusEvent(BaseModel):

    type: str = "status"

    status: str

    connections: int