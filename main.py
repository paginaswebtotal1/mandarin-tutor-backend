import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Ming Laoshi")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

api_key = os.environ.get("GEMINI_API_KEY", "").strip()
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """Eres Ming Lǎoshī (明老师), tutora paciente y amable de chino mandarín."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    level: str = "hsk1"

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        if not api_key:
            raise HTTPException(500, "GEMINI_API_KEY no configurada")

        config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)

        contents = []
        for m in req.messages[-12:]:
            role = "user" if m.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(m.content)]))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config
        )
        return {"reply": response.text}

    except Exception as e:
        print("ERROR:", str(e))
        if "429" in str(e):
            raise HTTPException(429, "Cuota agotada")
        raise HTTPException(500, "Error interno")
