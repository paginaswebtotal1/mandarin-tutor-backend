import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# Importamos el nuevo SDK oficial de Google GenAI
from google import genai
from google.genai import types

app = FastAPI(title="Ming Laoshi - Mandarin Tutor API")

# Configuración de CORS estricta pero abierta para tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización segura del cliente de Google
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
        # Validar que la API Key exista antes de hacer la petición
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY no configurada en Render.")

        # Configuramos las instrucciones del sistema y el nivel dinámico que viene de tu index.html
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + f"\n\nNivel actual del estudiante: {req.level.upper()}"
        )

        # Formateamos el contenido adaptando los roles del frontend ('assistant') a los de Gemini ('model')
        formatted_contents = []
        for msg in req.messages:
            # Tu index.html usa 'assistant', pero Gemini exige 'model'
            role = "user" if msg.role == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )

        # Si por alguna razón el historial llegó vacío, enviamos una estructura básica segura
        if not formatted_contents:
            raise HTTPException(status_code=400, detail="La lista de mensajes no puede estar vacía.")

        # Llamada oficial al modelo de última generación
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=formatted_contents,
            config=config
        )

        return {"reply": response.text}

    except Exception as e:
        # Esto imprimirá el error exacto en los logs de Render para que lo podamos ver
        print(f"ERROR CRÍTICO INTERNO: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))