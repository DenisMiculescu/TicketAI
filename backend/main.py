from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TicketAI API")


class Ticket(BaseModel):
    description: str


@app.get("/")
def home():
    return {"message": "TicketAI API is running"}


@app.post("/tickets/analyse")
def analyse_ticket(ticket: Ticket):
    return {
        "description": ticket.description,
        "category": "Software",
        "priority": "Medium",
        "team": "IT Support"
    }
