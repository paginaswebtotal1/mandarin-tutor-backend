import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# Usamos el SDK oficial y moderno de Google GenAI
from google import genai
from google.genai import types

app = FastAPI(title="Ming Laoshi - Mandarin Tutor API")

# Configuración de CORS abierta para conectar con tu frontend en Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización segura de la clave de Gemini
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
        # Validación de seguridad de la API Key
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY no configurada en las variables de entorno de Render.")

        # Configuración de las instrucciones del sistema con el nivel dinámico enviado por el frontend
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + f"\n\nNivel actual del estudiante: {req.level.upper()}"
        )

        formatted_contents = []
        
        # Filtro de seguridad: Gemini exige que las conversaciones inicien estrictamente con el rol 'user'
        valid_messages = req.messages
        while valid_messages and valid_messages[0].role != "user":
            valid_messages.pop(0)

        # Mapeo y traducción de roles limpia para Gemini 2.0
        for msg in valid_messages:
            role = "user" if msg.role == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        # Si el historial se queda vacío tras la limpieza, lanzamos una excepción controlada
        if not formatted_contents:
            raise HTTPException(status_code=400, detail="El historial de chat no puede estar vacío y debe comenzar con un mensaje del usuario.")

        # Llamada oficial al modelo de última generación de Google
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=formatted_contents,
            config=config
        )

        return {"reply": response.text}

    except Exception as e:
        # Esto nos permitirá auditar el error exacto directamente desde la consola negra de Render
        print(f"ERROR CRÍTICO EN CHAT: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))