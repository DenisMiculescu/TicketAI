
import os
import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from prompts import SYSTEM_PROMPT
from schemas import Ticket, TicketClassification

load_dotenv()

app = FastAPI(title="TicketAI API")

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")


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
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
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

        result = TicketClassification.model_validate_json(analysis)

        return {
            "description": ticket.description,
            "classification": result.model_dump()
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

    except ValidationError as e:
        print("AI validation error:", e.errors(include_input=False))

        raise HTTPException(
            status_code=502,
            detail="AI returned an invalid ticket classification"
        )

    except (ValueError, KeyError, IndexError, TypeError) as e:
        print("Response parsing error:", str(e))

        raise HTTPException(
            status_code=502,
            detail="Invalid response from AI model"
        )
