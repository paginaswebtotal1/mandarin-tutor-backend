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

api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

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
- Responde siempre en español salvo que el usuario pida otra cosa."""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    level: str = "hsk1"

@app.get("/")
def root():
    return {"status": "ok", "message": "API de Ming Laoshi corriendo"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY no encontrada.")

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + f"\n\nNivel actual del estudiante: {req.level.upper()}"
        )

        formatted_contents = []
        
        # FILTRO DE SEGURIDAD: Gemini exige que el historial EMPIECE por el usuario ('user')
        # Si el primer mensaje de la lista es un saludo del asistente, lo ignoramos para evitar el Error 500
        valid_messages = req.messages
        while valid_messages and valid_messages[0].role != "user":
            valid_messages.pop(0)

        # Mapeamos los mensajes limpiando los roles
        for msg in valid_messages:
            role = "user" if msg.role == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        # Si el historial quedó vacío tras limpiar o no venían mensajes, lanzamos error controlado
        if not formatted_contents:
            raise HTTPException(status_code=400, detail="El historial debe empezar con un mensaje del usuario.")

        # Llamada a Gemini 2.0 Flash
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=formatted_contents,
            config=config
        )

        return {"reply": response.text}

    except Exception as e:
        # Esto nos dejará ver en los logs de Render exactamente qué falló si no es el historial
        print(f"ERROR GENERANDO CONTENIDO: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))