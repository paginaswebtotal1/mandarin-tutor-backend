from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
import os

app = FastAPI(title="Mandarin Tutor API")

# CORS - permite que el frontend en Vercel llame al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción pon tu URL de Vercel aquí
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura Gemini con tu API key (la pones en Render como variable de entorno)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

SYSTEM_PROMPT = """Eres Ming Lǎoshī (明老师), tutora experta de chino mandarín para hispanohablantes.
Enseñas desde cero hasta HSK 6 de forma progresiva y motivadora.

FORMATO OBLIGATORIO en cada respuesta:
- Para palabras/frases chinas usa SIEMPRE:
  [CHINO]: carácter(es)
  [PINYIN]: transcripción con tonos
  [ESPAÑOL]: traducción
  [PRONUNCIACION]: tip para hispanohablantes

- Si el estudiante escribe en chino:
  [CORRECCION]: "escribiste X, lo correcto es Y porque..."
  o [CORRECTO]: "¡Perfecto! X significa..."

- Estructura lecciones con: concepto, 3-4 ejemplos, mini-ejercicio al final
- Sé cálida, paciente y motivadora
- Incluye curiosidades culturales relevantes
- Responde siempre en español salvo que el usuario pida otra cosa
"""

class Message(BaseModel):
    role: str  # "user" o "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    level: str = "hsk1"

@app.get("/")
def root():
    return {"status": "ok", "message": "Mandarin Tutor API funcionando"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",  # Gratis con límites generosos
            system_instruction=SYSTEM_PROMPT + f"\nNivel del estudiante: {req.level}"
        )

        # Convierte el historial al formato de Gemini
        history = []
        messages = req.messages[:-1]  # Todo menos el último
        for msg in messages:
            history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content]
            })

        chat_session = model.start_chat(history=history)

        # Último mensaje del usuario
        last_message = req.messages[-1].content
        response = chat_session.send_message(last_message)

        return {"reply": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
