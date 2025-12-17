# Día 1: Presentando *El Gemelo*

## Tu Gemelo Digital de IA cobra vida

Bienvenido a la Semana 2. Esta semana, construirás y desplegarás tu propio Gemelo Digital de IA: una IA conversacional que te representa a ti (o a cualquier persona que elijas) y que puede interactuar con los visitantes en tu nombre. Para el final de esta semana, tu twin estará desplegado en AWS, completo con memoria, personalidad e infraestructura profesional en la nube.

Hoy, comenzaremos construyendo una versión local que muestra un desafío fundamental en las aplicaciones de IA: la importancia de la memoria de la conversación.

## Lo que aprenderás hoy

- **Next.js App Router** vs arquitectura Pages Router
- **Construir una interfaz de chat** con React y Tailwind CSS
- **Crear un backend FastAPI** para conversaciones de IA
- **Entender la IA sin estado** y por qué la memoria importa
- **Implementar memoria basada en archivos** para la persistencia de conversaciones

## Entendiendo App Router vs Pages Router

En la Semana 1, usamos Next.js con el **Pages Router**. Esta semana, estamos usando el **App Router**. Esto es lo que necesitas saber:

### Pages Router (Semana 1)
- Los archivos en el directorio `pages/` se convierten en rutas
- `pages/index.tsx` → `/`
- `pages/product.tsx` → `/product`
- Usa `getServerSideProps` para la obtención de datos

### App Router (Semana 2)
- Los archivos en el directorio `app/` definen rutas
- `app/page.tsx` → `/`
- `app/about/page.tsx` → `/about`
- Usa React Server Components por defecto
- Más moderno, mejor rendimiento, recomendado para proyectos nuevos

Para nuestros propósitos, la diferencia principal es la estructura del proyecto: ¡el código React que escribas será muy similar!

## Parte 1: Configuración del proyecto

### Paso 1: Crea la estructura de tu proyecto

Abre Cursor (o tu IDE preferido) y crea un proyecto nuevo:

1. **Windows/Mac/Linux:** File → Open Folder → Crea una carpeta nueva llamada `twin`
2. Abre la carpeta `twin` en Cursor

### Paso 2: Crea directorios del proyecto

En el explorador de archivos de Cursor (la barra lateral izquierda):

1. Haz clic derecho en el espacio vacío debajo de tu carpeta `twin`
2. Selecciona **New Folder** y nómbralo `backend`
3. Haz clic derecho de nuevo y selecciona **New Folder** y nómbralo `memory`

Tu estructura de proyecto ahora debería verse así:
```
twin/
├── backend/
└── memory/
```

### Paso 3: Inicializa el frontend

Vamos a crear una app de Next.js con App Router.

Abre una terminal en Cursor (Terminal → New Terminal o Ctrl+` / Cmd+`):

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
```

Cuando se te solicite, acepta todas las opciones predeterminadas presionando Enter.

Después de que termine, crea un directorio components usando el explorador de archivos de Cursor:

1. En la barra lateral izquierda, expande la carpeta `frontend`
2. Haz clic derecho en la carpeta `frontend`
3. Selecciona **New Folder** y nómbralo `components`

✅ **Punto de control**: Tu estructura de proyecto debería verse así:
```
twin/
├── backend/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   └── (varios archivos de configuración)
└── memory/
```

## Parte 2: Instala el gestor de paquetes de Python

Usaremos `uv`, un gestor de paquetes moderno y rápido para Python que es mucho más veloz que pip.

### Instala uv

Visita la guía de instalación de uv: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

**Instalación rápida:**

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Después de la instalación, cierra y vuelve a abrir tu terminal, luego verifica:
```bash
uv --version
```

Deberías ver un número de versión como `uv 0.8.18` o similar.

## Parte 3: Crea la API del backend

### Paso 1: Crea el archivo de requisitos

Crea `backend/requirements.txt`:

```
fastapi
uvicorn
openai
python-dotenv
python-multipart
```

### Paso 2: Crea la configuración de entorno

Crea `backend/.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
CORS_ORIGINS=http://localhost:3000
```

Reemplaza `your_openai_api_key_here` con tu API key real de OpenAI de la Semana 1.

¡Recuerda guardar el archivo!

Además, es una buena práctica en caso de que alguna vez decidas subir este repo a GitHub:

1. Crea un archivo nuevo llamado .gitignore en la raíz del proyecto (`twin`)
2. Agrega una sola línea con ".env"
3. Guarda

### Paso 3: Crea la personalidad de tu Gemelo Digital

Crea `backend/me.txt` con una descripción de quién representa tu Gemelo Digital. Por ejemplo:

```
Eres un chatbot que actúa como un "Gemelo Digital", representando a [Tu Nombre] en el sitio web de [Tu Nombre],
e interactuando con los visitantes del sitio.

Tu objetivo es responder preguntas actuando como [Tu Nombre], según tus conocimientos y con base en el contexto proporcionado.

[Tu Nombre] es [tu profesión/rol]. [Agrega 2-3 frases sobre experiencia, formación o intereses]
```

¡Personaliza esto para representarte a ti mismo o a cualquier persona cuya persona quieras que tu twin encarne!

### Paso 4: Crea el servidor FastAPI (sin memoria)

Crea `backend/server.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional
import uuid

# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI()


# Load personality details
def load_personality():
    with open("me.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


PERSONALITY = load_personality()


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "AI Digital Twin API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Create system message with personality
        # NOTE: No memory - each request is independent!
        messages = [
            {"role": "system", "content": PERSONALITY},
            {"role": "user", "content": request.message},
        ]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages
        )

        return ChatResponse(
            response=response.choices[0].message.content, 
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Parte 4: Crea la interfaz frontend

### Paso 1: Crea el componente Twin

Crea `frontend/components/twin.tsx`:

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function Twin() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId || undefined,
                }),
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();

            if (!sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            // Add error message
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50 rounded-lg shadow-lg">
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white p-4 rounded-t-lg">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Bot className="w-6 h-6" />
                    AI Digital Twin
                </h2>
                <p className="text-sm text-slate-300 mt-1">Your AI course companion</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-8">
                        <Bot className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        <p>Hello! I&apos;m your Digital Twin.</p>
                        <p className="text-sm mt-2">Ask me anything about AI deployment!</p>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-3 ${
                            message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                        {message.role === 'assistant' && (
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                                    <Bot className="w-5 h-5 text-white" />
                                </div>
                            </div>
                        )}

                        <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                                message.role === 'user'
                                    ? 'bg-slate-700 text-white'
                                    : 'bg-white border border-gray-200 text-gray-800'
                            }`}
                        >
                            <p className="whitespace-pre-wrap">{message.content}</p>
                            <p
                                className={`text-xs mt-1 ${
                                    message.role === 'user' ? 'text-slate-300' : 'text-gray-500'
                                }`}
                            >
                                {message.timestamp.toLocaleTimeString()}
                            </p>
                        </div>

                        {message.role === 'user' && (
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                                    <User className="w-5 h-5 text-white" />
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3 justify-start">
                        <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Type your message..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-600 focus:border-transparent text-gray-800"
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                        className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
```

### Paso 2: Instala las dependencias requeridas

El componente Twin usa lucide-react para íconos. Instálalo:

```bash
cd frontend
npm install lucide-react
cd ..
```

### Paso 3: Actualiza la página principal

Reemplaza el contenido de `frontend/app/page.tsx`:

```typescript
import Twin from '@/components/twin';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
            AI in Production
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Deploy your Digital Twin to the cloud
          </p>

          <div className="h-[600px]">
            <Twin />
          </div>

          <footer className="mt-8 text-center text-sm text-gray-500">
            <p>Week 2: Building Your Digital Twin</p>
          </footer>
        </div>
      </div>
    </main>
  );
}
```

### Paso 4: Corrige la configuración de Tailwind v4

Next.js 15.5 viene con Tailwind CSS v4, que tiene un enfoque de configuración diferente. Necesitamos actualizar dos archivos:

Primero, actualiza `frontend/postcss.config.mjs`:

```javascript
export default {
    plugins: {
        '@tailwindcss/postcss': {},
    },
}
```

### Paso 5: Actualiza los estilos globales para Tailwind v4

Reemplaza el contenido de `frontend/app/globals.css`:

```css
@import 'tailwindcss';

/* Smooth scrolling animation keyframe */
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite;
}

.delay-100 {
  animation-delay: 0.1s;
}

.delay-200 {
  animation-delay: 0.2s;
}
```

## Parte 5: Prueba tu Gemelo Digital (sin memoria)

### Paso 1: Inicia el servidor backend

Abre una terminal nueva en Cursor (Terminal → New Terminal):

```bash
cd backend
uv init --bare
uv python pin 3.12
uv add -r requirements.txt
uv run uvicorn server:app --reload
```

Deberías ver algo como esto al final:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Paso 2: Inicia el servidor de desarrollo frontend

Abre otra terminal nueva:

```bash
cd frontend
npm run dev
```

Deberías ver:
```
▲ Next.js 15.x.x
Local: http://localhost:3000
```

### Paso 3: Experimenta el problema de la memoria

1. Abre tu navegador y ve a `http://localhost:3000`
2. Deberías ver la interfaz de tu Gemelo Digital
3. Prueba esta conversación:
   - **Tú:** "Hi! My name is Alex"
   - **Twin:** (responde con un saludo)
   - **Tú:** "What's my name?"
   - **Twin:** (¡no recordará tu nombre!)

**¿Qué está pasando?** ¡Tu twin no tiene memoria! Cada mensaje se procesa de manera independiente sin contexto de mensajes previos. Es como conocer a alguien nuevo cada vez que hablas con él.

## Parte 6: Añadiendo memoria a tu Twin

Ahora arreglemos esto añadiendo memoria de conversación que persista en archivos.

### Paso 1: Actualiza el backend con soporte de memoria

Reemplaza tu `backend/server.py` con esta versión mejorada:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
from pathlib import Path

# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI()

# Memory directory
MEMORY_DIR = Path("../memory")
MEMORY_DIR.mkdir(exist_ok=True)


# Load personality details
def load_personality():
    with open("me.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


PERSONALITY = load_personality()


# Memory functions
def load_conversation(session_id: str) -> List[Dict]:
    """Load conversation history from file"""
    file_path = MEMORY_DIR / f"{session_id}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history to file"""
    file_path = MEMORY_DIR / f"{session_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "AI Digital Twin API with Memory"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Load conversation history
        conversation = load_conversation(session_id)
        
        # Build messages with history
        messages = [{"role": "system", "content": PERSONALITY}]
        
        # Add conversation history
        for msg in conversation:
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        conversation.append({"role": "user", "content": request.message})
        conversation.append({"role": "assistant", "content": assistant_response})
        
        # Save updated conversation
        save_conversation(session_id, conversation)
        
        return ChatResponse(
            response=assistant_response,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    """List all conversation sessions"""
    sessions = []
    for file_path in MEMORY_DIR.glob("*.json"):
        session_id = file_path.stem
        with open(file_path, "r", encoding="utf-8") as f:
            conversation = json.load(f)
            sessions.append({
                "session_id": session_id,
                "message_count": len(conversation),
                "last_message": conversation[-1]["content"] if conversation else None
            })
    return {"sessions": sessions}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Paso 2: Reinicia el servidor backend

Detén el servidor backend (Ctrl+C en la terminal) y reinícialo:

```bash
uv run uvicorn server:app --reload
```

### Paso 3: Prueba la persistencia de la memoria

1. Refresca tu navegador en `http://localhost:3000`
2. Ten una conversación:
   - **Tú:** "Hi! My name is Alex and I love Python"
   - **Twin:** (responde con un saludo)
   - **Tú:** "What's my name and what do I love?"
   - **Twin:** (¡recuerda que te llamas Alex y que te encanta Python!)

3. Revisa la carpeta memory: ¡verás archivos JSON que contienen tus conversaciones!

```bash
ls ../memory/
```

Verás archivos como `abc123-def456-....json` que contienen el historial completo de la conversación.

## Entendiendo lo que construimos

### La arquitectura

```
Navegador del usuario → Frontend Next.js → Backend FastAPI → OpenAI API
                     ↑                    ↓
                     └──── Archivos de memoria ←─┘
```

### Componentes clave

1. **Frontend (Next.js con App Router)**
   - `app/page.tsx`: Página principal usando Server Components
   - `components/twin.tsx`: Componente de chat del lado del cliente
   - Actualizaciones de UI en tiempo real con estado de React

2. **Backend (FastAPI)**
   - Endpoints RESTful
   - Integración con OpenAI
   - Persistencia de memoria basada en archivos
   - Gestión de sesiones

3. **Sistema de memoria**
   - Archivos JSON almacenan el historial de conversación
   - Cada sesión tiene su propio archivo
   - Las conversaciones persisten a través de reinicios del servidor

## ¡Felicidades! 🎉

Has construido tu primer Gemelo Digital de IA con:
- ✅ Una interfaz de chat responsiva
- ✅ Integración con la API de OpenAI
- ✅ Memoria de conversación persistente
- ✅ Gestión de sesiones
- ✅ Estructura profesional de proyecto

### Lo que aprendiste

1. **La importancia de la memoria en aplicaciones de IA**: sin memoria, las interacciones de IA se sienten desconectadas y frustrantes
2. **Persistencia basada en archivos**: una forma simple pero efectiva de almacenar el historial de conversaciones
3. **Gestión de sesiones**: cómo rastrear conversaciones diferentes
4. **Desarrollo de IA full-stack**: conectar frontend, backend y servicios de IA

## Solución de problemas

### Error "Connection refused"
- Asegúrate de que tanto el servidor backend como el frontend estén ejecutándose
- Verifica que el backend esté en el puerto 8000 y el frontend en el puerto 3000

### Errores de la API de OpenAI
- Verifica que tu API key sea correcta en `backend/.env`
- Revisa que tengas créditos en tu cuenta de OpenAI

### La memoria no persiste
- Asegúrate de que el directorio `memory/` exista
- Verifica los permisos de archivo si estás en Linux/Mac
- Busca archivos `.json` en el directorio memory

### El frontend no se actualiza
- Limpia la cache del navegador
- Asegúrate de haber guardado todos los archivos
- Revisa la consola del navegador para ver errores

## Próximos pasos

Mañana (Día 2), vamos a:
- Añadir personalización con datos y documentos personalizados
- Desplegar el backend en AWS Lambda
- Configurar CloudFront para distribución global
- Crear una arquitectura lista para producción

¡Tu Gemelo Digital apenas está comenzando! Mañana le daremos más personalidad y lo desplegaremos en la nube.

## Recursos

- [Documentación del App Router de Next.js](https://nextjs.org/docs/app)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Referencia de la API de OpenAI](https://platform.openai.com/docs/api-reference)
- [Documentación de uv](https://docs.astral.sh/uv/)

¿Listo para el Día 2? ¡Tu twin está a punto de volverse mucho más interesante! 🚀