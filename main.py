import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Ming Laoshi - Mandarin Tutor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.environ.get("GEMINI_API_KEY", "").strip()
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """Eres Ming Lǎoshī (明老师), tutora amable de chino mandarín."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    level: str = "hsk1"

@app.get("/")
def root():
    return {"status": "ok", "message": "Ming Laoshi API running"}

@app.get("/health")
def health():
    return {"status": "healthy", "has_key": bool(api_key)}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY no configurada")

        config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)

        contents = []
        for msg in req.messages[-12:]:
            role = "user" if msg.role == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)]
            ))

        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=contents,
            config=config
        )

        return {"reply": response.text}

    except Exception as e:
        error = str(e)
        print(f"ERROR CRÍTICO: {error}")
        if "429" in error:
            raise HTTPException(429, "Cuota agotada")
        raise HTTPException(500, "Error interno del servidor")
