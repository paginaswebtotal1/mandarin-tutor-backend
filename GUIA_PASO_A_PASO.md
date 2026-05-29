# 🇨🇳 Guía Completa: Publicar Tutor de Chino Mandarín
## GitHub → Render (Backend) → Vercel (Frontend)
### Todo gratis, con HTTPS/SSL incluido

---

## ANTES DE EMPEZAR — Instala Git (si no lo tienes)

1. Ve a https://git-scm.com/downloads
2. Descarga e instala para tu sistema operativo
3. Abre la terminal (en Windows: busca "Git Bash" o "CMD")
4. Configura tu identidad (hazlo UNA sola vez):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

---

## PASO 1 — OBTÉN TU API KEY DE GEMINI (GRATIS)

1. Ve a: https://aistudio.google.com
2. Haz clic en "Get API Key" (arriba a la derecha)
3. Clic en "Create API Key"
4. Selecciona "Create API key in new project"
5. **COPIA y GUARDA esa clave** — la necesitas en el Paso 4
   - Se ve así: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
6. El plan gratuito incluye: 15 RPM, 1 millón tokens/día — MÁS que suficiente

---

## PASO 2 — SUBE EL BACKEND A GITHUB

### 2.1 — Crea el repositorio del backend

1. Ve a https://github.com y haz login
2. Clic en el botón verde **"New"** (o el símbolo +)
3. Nombre del repositorio: `mandarin-tutor-backend`
4. Selecciona **"Public"** (necesario para Render gratuito)
5. **NO** marques ninguna casilla (sin README, sin .gitignore)
6. Clic en **"Create repository"**
7. GitHub te mostrará una página con instrucciones — **déjala abierta**

### 2.2 — Sube los archivos desde tu computador

Abre la terminal en la carpeta `backend` del proyecto y ejecuta:

```bash
# Entra a la carpeta del backend
cd ruta/a/mandarin-tutor/backend

# Inicializa git
git init

# Agrega todos los archivos
git add .

# Primer commit
git commit -m "primer commit: backend mandarin tutor"

# Conecta con GitHub (CAMBIA por tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/mandarin-tutor-backend.git

# Sube el código
git branch -M main
git push -u origin main
```

Cuando te pida contraseña, GitHub ya no acepta contraseñas — necesitas un token:
- Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- "Generate new token" → marca `repo` → genera → copia el token
- Usa ese token como contraseña en la terminal

✅ **Listo**: ve a github.com/TU_USUARIO/mandarin-tutor-backend y verás tus archivos

---

## PASO 3 — DESPLIEGA EL BACKEND EN RENDER

### SSL/HTTPS: Render lo da AUTOMÁTICO y GRATIS 🔒

1. Ve a https://render.com y haz login
2. Clic en **"New +"** (botón azul arriba a la derecha)
3. Selecciona **"Web Service"**
4. En la sección "Connect a repository":
   - Clic en **"Connect GitHub"** si no lo has hecho
   - Autoriza Render para acceder a tus repos
   - Busca y selecciona **`mandarin-tutor-backend`**
5. Completa el formulario:

   | Campo | Valor |
   |-------|-------|
   | Name | `mandarin-tutor-api` |
   | Region | `Oregon (US West)` (o el más cercano) |
   | Branch | `main` |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | **Free** (selecciona el gratuito) |

6. Baja hasta **"Environment Variables"**
7. Clic en **"Add Environment Variable"**:
   - Key: `GEMINI_API_KEY`
   - Value: (pega tu clave de Gemini del Paso 1)
8. Clic en **"Create Web Service"**

### ⏳ Espera 3-5 minutos mientras Render construye tu app

- Verás logs en tiempo real
- Cuando diga **"Your service is live"** habrás terminado
- Tu URL será algo como: `https://mandarin-tutor-api.onrender.com`
- **COPIA ESA URL** — la necesitas en el siguiente paso

### ⚠️ IMPORTANTE sobre el plan gratuito de Render:
El servicio gratuito "duerme" después de 15 minutos sin uso.
La primera petición tarda ~30 segundos en "despertar". Es normal.

---

## PASO 4 — ACTUALIZA LA URL EN EL FRONTEND

Abre el archivo `frontend/index.html` y busca esta línea:

```javascript
: 'https://TU-APP.onrender.com';  // ← CAMBIA ESTO
```

Cámbiala por tu URL real de Render:

```javascript
: 'https://mandarin-tutor-api.onrender.com';  // ← tu URL real
```

Guarda el archivo.

---

## PASO 5 — SUBE EL FRONTEND A GITHUB

### 5.1 — Crea el repositorio del frontend

1. Ve a https://github.com
2. Clic en **"New"**
3. Nombre: `mandarin-tutor-frontend`
4. Selecciona **"Public"**
5. Clic en **"Create repository"**

### 5.2 — Sube los archivos

```bash
# Entra a la carpeta del frontend
cd ruta/a/mandarin-tutor/frontend

# Inicializa git
git init

# Agrega todos los archivos
git add .

# Primer commit
git commit -m "primer commit: frontend mandarin tutor"

# Conecta con GitHub (CAMBIA por tu usuario)
git remote add origin https://github.com/TU_USUARIO/mandarin-tutor-frontend.git

# Sube
git branch -M main
git push -u origin main
```

✅ **Listo**: ve a github.com/TU_USUARIO/mandarin-tutor-frontend

---

## PASO 6 — DESPLIEGA EL FRONTEND EN VERCEL

### SSL/HTTPS: Vercel lo da AUTOMÁTICO y GRATIS 🔒

1. Ve a https://vercel.com y haz login (puedes entrar con tu cuenta de GitHub)
2. Clic en **"Add New..."** → **"Project"**
3. En "Import Git Repository":
   - Verás tu lista de repos de GitHub
   - Busca **`mandarin-tutor-frontend`**
   - Clic en **"Import"**
4. En la pantalla de configuración:
   - Project Name: `mandarin-tutor` (o el que quieras)
   - Framework Preset: **"Other"** (no es un framework)
   - Root Directory: deja `.` (punto)
   - Build & Output Settings: deja todo vacío/default
5. Clic en **"Deploy"**

### ⏳ Espera 1-2 minutos

- Vercel construye y publica automáticamente
- Tu URL pública será: `https://mandarin-tutor.vercel.app`
- También tendrá HTTPS/SSL automático

---

## RESULTADO FINAL 🎉

| Componente | URL | SSL |
|------------|-----|-----|
| **Frontend** | `https://mandarin-tutor.vercel.app` | ✅ Automático |
| **Backend API** | `https://mandarin-tutor-api.onrender.com` | ✅ Automático |

---

## CÓMO ACTUALIZAR EL CÓDIGO EN EL FUTURO

Cada vez que cambies algo, solo ejecuta:

```bash
# En la carpeta que modificaste (backend o frontend)
git add .
git commit -m "descripción del cambio"
git push
```

**Render y Vercel detectan el push automáticamente y re-despliegan en minutos.**

---

## ESTRUCTURA FINAL DEL PROYECTO

```
mandarin-tutor/
│
├── backend/                    → Subido a GitHub → Render
│   ├── main.py                 → Lógica de la API con Gemini
│   ├── requirements.txt        → Dependencias Python
│   ├── Procfile                → Comando de inicio
│   ├── render.yaml             → Config de Render
│   └── .gitignore
│
└── frontend/                   → Subido a GitHub → Vercel
    ├── index.html              → App completa (avatar + chat)
    └── vercel.json             → Config de Vercel
```

---

## SOLUCIÓN DE PROBLEMAS COMUNES

**❌ "Error: 401 Unauthorized" en Render**
→ Tu GEMINI_API_KEY está mal. Ve a Render → Environment → verifica la clave.

**❌ El chat no responde / "API desconectada"**
→ El servicio de Render está durmiendo. Espera 30 segundos y reintenta.

**❌ "CORS error" en el navegador**
→ Verifica que la URL en `index.html` sea exactamente la de Render (sin barra al final).

**❌ "Module not found" en Render**
→ Asegúrate de que `requirements.txt` está en la raíz del repo del backend.

**❌ Git pide contraseña y no acepta la de GitHub**
→ Usa un Personal Access Token (ver Paso 2.2 arriba).

---

## PARA TU HOJA DE VIDA 📄

Puedes describir este proyecto así:

> **Tutor Interactivo de Chino Mandarín con IA** | Python · FastAPI · Gemini AI · HTML/CSS/JS
> Aplicación web full-stack con avatar animado e IA conversacional para aprendizaje de chino mandarín.
> Sistema de enseñanza progresiva HSK 1-6 con corrección automática y síntesis de voz.
> Desplegado en Render (backend) y Vercel (frontend) con CI/CD automático vía GitHub.
> URL: https://mandarin-tutor.vercel.app

---

*Guía creada para el proyecto Mandarin AI Tutor · Ming Lǎoshī 明老师*
