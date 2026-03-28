from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ConversationRecord(BaseModel):
    message_id: str = Field(..., min_length=3)
    user_id: str = Field(..., min_length=3)
    campaign_id: str = Field(..., min_length=3)
    intent: Literal['pricing', 'discount', 'support', 'product', 'renewal', 'upsell']
    message: str = Field(..., min_length=1)
    timestamp: datetime

    @field_validator('message')
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError('message is empty after trim')
        return cleaned
