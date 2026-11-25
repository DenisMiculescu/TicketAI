from typing import Literal
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    description: str = Field(min_length=1, max_length=5000)


class TicketClassification(BaseModel):
    category: Literal[
        "Network",
        "Hardware",
        "Software",
        "Database",
        "Security",
        "Other"
    ]

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    team: Literal[
        "Network Support",
        "IT Support",
        "Application Support",
        "Database Administration",
        "Security Operations"
    ]

    summary: str = Field(min_length=1)
    suggested_response: str = Field(min_length=1)
