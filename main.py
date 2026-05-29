import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Ming Laoshi")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "")
)

SYSTEM_PROMPT = """Eres Ming Lǎoshī (明老师), tutora experta de chino mandarín para hispanohablantes. Enseñas desde cero hasta HSK 6. FORMATO OBLIGATORIO: Para palabras chinas usa [CHINO]: [PINYIN]: [ESPAÑOL]: [PRONUNCIACION]:. Si el estudiante escribe en chino usa [CORRECCION]: o [CORRECTO]:. Sé cálida y motivadora. Responde siempre en español."""

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
        messages = [{"role": "system", "content": SYSTEM_PROMPT + f" Nivel del estudiante: {req.level}"}]
        for m in req.messages[-12:]:
            messages.append({"role": m.role, "content": m.content})

        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=messages
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(500, str(e))