
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="TicketAI API")

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")


class Ticket(BaseModel):
    description: str = Field(min_length=1)


@app.get("/")
def home():
    return {"message": "TicketAI API is running"}


@app.post("/tickets/analyse")
async def analyse_ticket(ticket: Ticket):

    if not API_KEY or not MODEL:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter configuration is missing"
        )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an IT support assistant. "
                    "Explain the likely issue in one short sentence. "
                    "Do not claim to know the root cause without evidence."
                )
            },
            {
                "role": "user",
                "content": ticket.description
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )

        response.raise_for_status()
        data = response.json()
        print("Model used:", data.get("model"))

        analysis = data["choices"][0]["message"]["content"]

        if not isinstance(analysis, str) or not analysis.strip():
            raise ValueError("Empty AI response")

        return {
            "description": ticket.description,
            "analysis": analysis
        }

    except httpx.HTTPStatusError as e:
        print("OpenRouter status:", e.response.status_code)
        print("OpenRouter response:", e.response.text)

        raise HTTPException(
            status_code=502,
            detail="OpenRouter returned an error"
        )

    except httpx.RequestError as e:
        print("Connection error:", type(e).__name__, str(e))

        raise HTTPException(
            status_code=502,
            detail="Unable to connect to OpenRouter"
        )

    except (ValueError, KeyError, IndexError, TypeError) as e:
        print("Response parsing error:", str(e))

        raise HTTPException(
            status_code=502,
            detail="Invalid response from AI model"
        )
