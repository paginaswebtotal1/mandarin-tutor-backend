# Reemplazar main.py (ejecuta este comando)
cat > main.py << 'EOF'
import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Ming Laoshi - Mandarin Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.environ.get("GEMINI_API_KEY", "").strip()
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """Eres Ming Lǎoshī (明老师), tutora experta de chino mandarín para hispanohablantes.
Enseñas de forma cálida, paciente y motivadora.

FORMATO OBLIGATORIO en cada respuesta:
[CHINO]: 
[PINYIN]: 
[ESPAÑOL]: 
[PRONUNCIACION]: 

Si hay error: [CORRECCION]: ...
Si está bien: [CORRECTO]: ..."""

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
    return {"status": "healthy", "has_key": bool(api_key)}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY no configurada.")

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + f"\nNivel: {req.level.upper()}"
        )

        valid_messages = [m for m in req.messages if m.role in ("user", "model")]
        while valid_messages and valid_messages[0].role != "user":
            valid_messages.pop(0)

        if not valid_messages:
            valid_messages = [Message(role="user", content="Hola")]

        contents = []
        for msg in valid_messages:
            role = "user" if msg.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config
        )

        return {"reply": response.text}

    except Exception as e:
        error_str = str(e)
        print(f"ERROR CRÍTICO EN CHAT: {error_str}")
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            raise HTTPException(status_code=429, detail="Cuota de Gemini agotada. Crea una nueva API Key.")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")