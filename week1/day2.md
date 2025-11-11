# 💼 SaaS – Creando una Aplicación de IA Full-Stack

## 🚀 Construye tu Primer Producto SaaS con Next.js y FastAPI

Hoy vas a crear una **aplicación full-stack completa** con un frontend en **React** y un backend en **Python**, todo desplegado en producción con **Vercel**. ⚡

---

## 🎯 Qué Vas a Construir

Un **Generador de Ideas de Negocio** — una aplicación SaaS impulsada por IA que:

* 💻 Tiene un frontend moderno con **Next.js** (usando *Pages Router* por estabilidad)
* 🧩 Usa **TypeScript** para mayor seguridad en el código
* 🔗 Se conecta a un backend con **FastAPI**
* ⚡ Transmite respuestas de la IA en tiempo real
* 📝 Muestra el contenido en **Markdown** de forma elegante
* 🌍 Se despliega fácilmente en producción

---

## 🧠 Requisitos Previos

* Haber completado el **Día 1** (ya deberías tener instalado **Node.js** y **Vercel CLI**)
* Tu **clave API de OpenAI** configurada

---

## 🏗️ Paso 1: Crea tu Proyecto de Next.js

### 🧰 Abre Cursor y Crea el Proyecto

1. Abre **Cursor**
2. Abre la terminal (*Terminal → New Terminal* o `Ctrl + \`` / `Cmd + ``)
3. Navega hasta la carpeta donde quieras crear el proyecto
4. Ejecuta el siguiente comando:

> ⚠️ Nota: Ligero cambio respecto a los vídeos. Estamos fijando la versión de Next.js a **15.5.6**, ya que en octubre de 2025 se lanzó la **versión 16.0.0**, y algunas librerías aún no son compatibles.

```bash
npx create-next-app@15.5.6 saas --typescript
```

Cuando te haga preguntas, responde así:

1. **Which linter would you like to use?** → Presiona **Enter** para **ESLint** (por defecto)
2. **Would you like to use Tailwind CSS?** → Escribe `y` y presiona **Enter**
3. **Would you like your code inside a `src/` directory?** → Escribe `n` y presiona **Enter**
4. **Would you like to use App Router? (recommended)** → Escribe `n` y presiona **Enter**
5. **Would you like to use Turbopack? (recommended)** → Escribe `n` y presiona **Enter**
6. **Would you like to customize the import alias?** → Escribe `n` y presiona **Enter**

Esto creará un nuevo proyecto de Next.js con:

* 🧭 **Pages Router** (el sistema de enrutamiento estable y probado)
* 🧑‍💻 **TypeScript** para detección temprana de errores
* 🧹 **ESLint** para mantener la calidad del código
* 🎨 **Tailwind CSS** para estilos rápidos y consistentes

---

### 📂 Abre tu Proyecto

1. En **Cursor**: ve a *File → Open Folder* y selecciona la carpeta **"saas"**
2. Verás varios archivos y carpetas generados automáticamente por Next.js

---

### 🧱 Estructura del Proyecto

Tu proyecto luce así:

```
saas/
├── pages/              # Directorio del Pages Router (aquí viven tus páginas)
│   ├── _app.tsx       # Envoltura principal de la aplicación
│   ├── _document.tsx  # Documento HTML personalizado
│   ├── index.tsx      # Página principal (ruta "/")
│   └── api/           # Rutas API de ejemplo (vamos a eliminarlo)
│       └── hello.ts
├── styles/            # Carpeta de estilos
│   └── globals.css    # Estilos globales + Tailwind
├── public/            # Archivos estáticos (imágenes, fuentes, etc.)
├── package.json       # Dependencias y scripts de Node.js
├── tsconfig.json      # Configuración de TypeScript
├── next.config.js     # Configuración de Next.js
└── node_modules/      # Paquetes instalados automáticamente
```

📘 **Explicación de archivos clave:**

* `pages/_app.tsx`: inicializa todas las páginas (ideal para estilos y proveedores globales).
* `pages/_document.tsx`: define la estructura base del HTML.
* `pages/index.tsx`: es tu página principal (lo que se ve en “/”).
* `styles/globals.css`: contiene los estilos globales con las importaciones de Tailwind.

---

### 🧹 Limpieza Inicial

Como usaremos **FastAPI** en lugar del API interno de Next.js, eliminaremos la carpeta `api`:

1. En el panel izquierdo de **Cursor**, busca la carpeta `pages/api`
2. Haz clic derecho sobre `api` → **Delete**
3. Confirma la eliminación

---

### 🎨 ¿Qué es Tailwind CSS?

**Tailwind CSS** es un framework de CSS orientado a utilidades. En lugar de escribir reglas personalizadas, aplicas clases predefinidas directamente en tu JSX.

Ejemplos:

* `bg-blue-500` → fondo azul
* `text-white` → texto blanco
* `p-4` → padding en todos los lados
* `rounded-lg` → esquinas redondeadas

✅ Esto acelera el desarrollo y mantiene un diseño coherente.

---

## ⚙️ Paso 2: Configura el Backend

### 📁 Crea la Carpeta del API

En el explorador de archivos de **Cursor**, crea una nueva carpeta en la raíz del proyecto:

* Clic derecho → **New Folder** → nómbrala **api**

---

### 📦 Crea las Dependencias de Python

Crea un nuevo archivo en la raíz del proyecto llamado `requirements.txt` con el siguiente contenido:

```
fastapi
uvicorn
openai
```

### Crea el Servidor API

Crea un nuevo fichero `api/index.py`:

```python
from fastapi import FastAPI  # type: ignore
from fastapi.responses import PlainTextResponse  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()

@app.get("/api", response_class=PlainTextResponse)
def idea():
    client = OpenAI()
    prompt = [{"role": "user", "content": "Dame nuevas ideas de negocio para agentes de IA"}]
    response = client.chat.completions.create(model="gpt-5-nano", messages=prompt)
    return response.choices[0].message.content
```

# 🧩 Paso 3: Crea tu Primera Página

### 💡 Entendiendo los *Client Components*

En **Next.js con Pages Router**, todos los componentes de página se ejecutan tanto en el servidor como en el cliente por defecto.
Pero como usaremos un **backend en Python con FastAPI** (y no las rutas API internas de Next.js), debemos indicar explícitamente que nuestros componentes se ejecuten **en el navegador**.

Esto se logra añadiendo la línea `"use client"` al principio del archivo.

Así conseguimos que:

* ⚙️ El componente se ejecute directamente en el navegador
* 🌐 El navegador realice las peticiones API al backend de Python
* 🚫 Next.js no actúe como intermediario entre el cliente y el backend

---

### 🏠 Crea la Página Principal

Abre el archivo `pages/index.tsx` y **reemplaza todo su contenido** por lo siguiente:

```typescript
"use client"

import { useEffect, useState } from 'react';

export default function Home() {
    const [idea, setIdea] = useState<string>('…loading');

    useEffect(() => {
        fetch('/api')
            .then(res => res.text())
            .then(setIdea)
            .catch(err => setIdea('Error: ' + err.message));
    }, []);

    return (
        <main className="p-8 font-sans">
            <h1 className="text-3xl font-bold mb-4">
                Business Idea Generator
            </h1>
            <div className="w-full max-w-2xl p-6 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm">
                <p className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                    {idea}
                </p>
            </div>
        </main>
    );
}
```

# 🚀 Paso 4: Configura y Despliega tu Proyecto SaaS

---

## 💡 Qué está pasando aquí

* `"use client"` 👉 le dice a **Next.js** que este componente se ejecuta directamente en el navegador.
* 🌐 El navegador realiza las peticiones **directamente a tu backend en Python (FastAPI)** en `/api`.
* ⚛️ Se usan *React Hooks* para gestionar el estado de la interfaz y obtener los datos de la API.
* ☁️ **Vercel** detecta automáticamente las rutas `/api` y las redirige a tu servidor Python — ¡sin necesidad de un archivo `vercel.json`!

---

## 🧱 Configura el Envoltorio de la Aplicación

El archivo `_app.tsx` se encarga de envolver todas las páginas de tu proyecto.
Aquí importaremos los estilos globales y los de **Tailwind CSS**.

Crea o reemplaza `pages/_app.tsx` con el siguiente contenido:

```typescript
import type { AppProps } from 'next/app';
import '../styles/globals.css';  // Importa los estilos de Tailwind

export default function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}
```

---

## 🧩 Configura el Documento HTML

El archivo `_document.tsx` define la estructura base del HTML, además de los metadatos del sitio.

Crea un nuevo archivo llamado `pages/_document.tsx` con el siguiente contenido:

```typescript
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="es">
      <Head>
        <title>Generador de Ideas de Negocio</title>
        <meta name="description" content="Generador de ideas de negocio con inteligencia artificial" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
```

---

## ⚙️ Paso 4: Configura tu Proyecto

📝 **Nota importante:**
No necesitas crear un archivo `vercel.json`.
Vercel detecta automáticamente tanto el proyecto **Next.js** como los archivos **Python** en la carpeta `api`, aplicando su configuración predeterminada.

---

## 🔗 Paso 5: Vincula tu Proyecto a Vercel

Vamos a crear y enlazar el proyecto local con tu cuenta de Vercel.

Ejecuta el siguiente comando en la terminal:

```bash
vercel link
```

Sigue las instrucciones:

* **Set up and link?** → Escribe `y` o presiona **Enter**
* **Which scope?** → Elige tu cuenta personal
* **Link to existing project?** → Escribe `n`
* **What's the name of your project?** → Escribe `saas`
* **In which directory is your code located?** → Presiona **Enter** (directorio actual)

💡 Esto crea el proyecto en Vercel y lo vincula automáticamente con tu carpeta local.

---

## 🔑 Paso 6: Añade tu Clave de API de OpenAI

Ahora que el proyecto está vinculado, añade tu **clave de API de OpenAI**:

```bash
vercel env add OPENAI_API_KEY
```

* Pega tu clave cuando te lo pida
* Selecciona **todas las opciones** (development, preview, production)

✅ Así tu clave quedará segura y accesible solo para el backend en producción.

---

## 🌍 Paso 7: Despliega y Prueba tu Aplicación

Despliega tu aplicación ejecutando:

```bash
vercel .
```

Cuando se te pregunte **"Set up and deploy?"**, responde **No** (ya vinculamos el proyecto antes).

🕹️ Una vez completado el despliegue, copia o haz clic en la URL que aparece, algo como:

```
https://saas-xxxxx.vercel.app
```

Deberías ver tu **Generador de Ideas de Negocio** mostrando una idea generada por inteligencia artificial 💡🤖

---

## 🧠 Nota Importante

Realizamos las pruebas directamente en la versión desplegada (no en local) para garantizar que:

* ✅ El **frontend de Next.js** y el **backend de FastAPI** funcionen correctamente juntos.
* ☁️ Todo el flujo (desde la interfaz hasta la IA) opere igual que en producción real.
--- 

# 🚀 Paso 8: Despliega tu Aplicación en Producción

Lleva tu aplicación completamente funcional al entorno de producción con un solo comando:

```bash
vercel --prod
```

Cuando termine, abre la **URL proporcionada** para ver tu aplicación **en vivo y lista para el mundo** 🌍✨

---

# ⚡ Parte 2: Añadiendo Streaming en Tiempo Real

Ahora mejoraremos tu app con **transmisión en vivo** (*real-time streaming*) y **renderizado de Markdown**.

---

## 🧩 Instala las Librerías de Markdown

Ejecuta en la terminal:

```bash
npm install react-markdown remark-gfm remark-breaks
```

Estas librerías te permitirán:

* ✅ Mostrar texto con formato Markdown (listas, negritas, encabezados, etc.)
* ✅ Soportar saltos de línea y estilo GitHub-Flavored Markdown

---

## 🎨 Actualiza el Frontend

Reemplaza **todo** el contenido de `pages/index.tsx` con:

```typescript
"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

export default function Home() {
    const [idea, setIdea] = useState<string>('…cargando');

    useEffect(() => {
        const evt = new EventSource('/api');
        let buffer = '';

        evt.onmessage = (e) => {
            buffer += e.data;
            setIdea(buffer);
        };
        evt.onerror = () => {
            console.error('Error de SSE, cerrando conexión');
            evt.close();
        };

        return () => { evt.close(); };
    }, []);

    return (
        <main className="p-8 font-sans bg-gradient-to-br from-blue-500 to-purple-600 min-h-screen text-white">
            <h1 className="text-4xl font-bold mb-6 text-center">
                💡 Generador de Ideas de Negocio
            </h1>

            <div className="w-full max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-md">
                <div className="prose prose-gray dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                        {idea}
                    </ReactMarkdown>
                </div>
            </div>
        </main>
    );
}
```

---

### 🧠 Explicación de las Clases de Tailwind

| Clase                           | Función                                                                       |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `prose`                         | Clase del plugin **Typography** que estiliza Markdown con tipografía elegante |
| `w-full max-w-2xl`              | Ocupa todo el ancho pero limita el máximo a un tamaño legible                 |
| `p-6`                           | Añade padding interno                                                         |
| `bg-white` / `dark:bg-gray-800` | Colores adaptados al modo claro/oscuro                                        |
| `border border-gray-300`        | Añade un borde sutil                                                          |
| `rounded-lg`                    | Bordes redondeados                                                            |
| `shadow-md`                     | Sombra suave para dar profundidad                                             |

🧩 **Nota:** seguimos necesitando `"use client"` al inicio del archivo porque las llamadas a la API se hacen directamente desde el navegador hacia el backend de FastAPI (sin pasar por el servidor de Next.js).

---

## 🧱 Instala el Plugin de Tipografía de Tailwind

La clase `prose` requiere el **plugin oficial de tipografía**.
Instálalo ejecutando:

```bash
npm install @tailwindcss/typography
```

Luego, abre tu archivo `tailwind.config.js` y agrega el plugin al final:

```javascript
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/typography')],
}
```

---

## ⚙️ Actualiza el Backend para Streaming

Reemplaza **todo el contenido** de `api/index.py` con:

```python
from fastapi import FastAPI  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()

@app.get("/api")
def idea():
    client = OpenAI()
    prompt = [{"role": "user", "content": "Inventa una nueva idea de negocio basada en agentes de IA"}]
    stream = client.chat.completions.create(model="gpt-5-nano", messages=prompt, stream=True)

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                for line in text.split("\n"):
                    yield f"data: {line}\n"
                yield "\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## 🔍 Prueba el Streaming

Despliega tu aplicación nuevamente para probar la transmisión en tiempo real:

```bash
vercel .
```

Abre la URL que aparece al final del despliegue.
🎉 Verás cómo el texto de la IA **aparece en tiempo real**, con formato Markdown perfecto.

---

# ✨ Parte 3: Estilizado Profesional

Vamos a pulir la apariencia visual de la app con estilos modernos y tipografía profesional.

---

## 🖋️ Corrige el Renderizado de Markdown

Por defecto, Tailwind CSS elimina algunos estilos base de HTML.
Para restaurarlos (y hacer que el Markdown se vea bien), añade esto **al final** de tu archivo `styles/globals.css`:


```css
@layer base {
  .markdown-content h1 {
    font-size: 2em;
    font-weight: bold;
    margin: 0.67em 0;
  }
  .markdown-content h2 {
    font-size: 1.5em;
    font-weight: bold;
    margin: 0.83em 0;
  }
  .markdown-content h3 {
    font-size: 1.17em;
    font-weight: bold;
    margin: 1em 0;
  }
  .markdown-content h4 {
    font-size: 1em;
    font-weight: bold;
    margin: 1.33em 0;
  }
  .markdown-content h5 {
    font-size: 0.83em;
    font-weight: bold;
    margin: 1.67em 0;
  }
  .markdown-content h6 {
    font-size: 0.67em;
    font-weight: bold;
    margin: 2.33em 0;
  }
  .markdown-content p {
    margin: 1em 0;
  }
  .markdown-content ul {
    list-style-type: disc;
    padding-left: 2em;
    margin: 1em 0;
  }
  .markdown-content ol {
    list-style-type: decimal;
    padding-left: 2em;
    margin: 1em 0;
  }
  .markdown-content li {
    margin: 0.25em 0;
  }
  .markdown-content strong {
    font-weight: bold;
  }
  .markdown-content em {
    font-style: italic;
  }
  .markdown-content hr {
    border: 0;
    border-top: 1px solid #e5e7eb;
    margin: 2em 0;
  }
}
```

Perfecto 💪 Vamos con la siguiente mejora: tu aplicación ahora generará **respuestas con formato Markdown avanzado**, usando encabezados, subtítulos y listas.

---

## 🧠 Actualiza el *prompt* del Backend

Abre el archivo `api/index.py` y reemplaza la línea del *prompt* por esta:

```python
prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]
```

Esto le indica a la IA que:

* 🧩 Devuelva la respuesta estructurada con **encabezados (`#`, `##`)**
* 🔹 Incluya **viñetas y subpuntos**
* 💅 Sea perfecta para mostrar con **ReactMarkdown**

---

## 🎨 Actualiza el Componente Principal

Reemplaza **todo el contenido** de `pages/index.tsx` con lo siguiente:

```typescript
"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

export default function Home() {
    const [idea, setIdea] = useState<string>('…loading');

    useEffect(() => {
        const evt = new EventSource('/api');
        let buffer = '';

        evt.onmessage = (e) => {
            buffer += e.data;
            setIdea(buffer);
        };
        evt.onerror = () => {
            console.error('SSE error, closing');
            evt.close();
        };

        return () => { evt.close(); };
    }, []);

    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            <div className="container mx-auto px-4 py-12">
                {/* Header */}
                <header className="text-center mb-12">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                        Generador de Ideas de Negocio
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                        Inovación con el poder de la IA en tus dedos 
                    </p>
                </header>

                {/* Content Card */}
                <div className="max-w-3xl mx-auto">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
                        {idea === '…loading' ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="animate-pulse text-gray-400">
                                    Generando tu idea de neegocio...
                                </div>
                            </div>
                        ) : (
                            <div className="markdown-content text-gray-700 dark:text-gray-300">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm, remarkBreaks]}
                                >
                                    {idea}
                                </ReactMarkdown>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </main>
    );
}
```
# 🌟 Paso 9: Despliega la Versión Final

Tu aplicación ya tiene todo lo necesario para lucir profesional y funcionar en producción.
¡Vamos a darle el toque final y subirla al mundo! 🚀

---

## 🎨 **Estilizado profesional con Tailwind CSS**

Aquí tienes un resumen de las clases de Tailwind que hacen que tu app se vea moderna, fluida y con un diseño de alto nivel:

| Clase                                                               | Descripción                                                                        |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `min-h-screen`                                                      | Ocupa toda la altura de la ventana del navegador                                   |
| `bg-gradient-to-br`                                                 | Aplica un degradado diagonal (ideal para fondos elegantes con soporte modo oscuro) |
| `container mx-auto`                                                 | Centra el contenido y mantiene márgenes responsivos                                |
| `text-5xl font-bold bg-gradient-to-r bg-clip-text text-transparent` | Crea un **efecto de texto con degradado**                                          |
| `rounded-2xl shadow-xl backdrop-blur-lg`                            | Crea un efecto **glassmorphism** (tarjeta translúcida con sombra y desenfoque)     |
| `animate-pulse`                                                     | Añade animación de “carga” mientras se transmite contenido                         |
| `markdown-content`                                                  | Clase personalizada que **restaura el estilo HTML del Markdown**                   |

✨ **Resultado final:**
Tu app combina **rendimiento, estilo y experiencia de usuario** profesional — ¡lista para mostrar a tus clientes o inversores!

---

## 🚀 Despliega tu Versión Final

Ejecuta en la terminal:

```bash
vercel --prod
```

Esto subirá tu versión definitiva a producción.
Cuando finalice, abre el enlace que aparece — algo como:

```
https://saas-xxxxx.vercel.app
```

Y disfruta de tu aplicación **totalmente funcional y en vivo** 🎉

---

# 🧠 ¡Enhorabuena!

Has construido un **SaaS completo impulsado por IA** con:

✅ Frontend moderno con **React + Next.js (Pages Router)**
✅ Tipado estático gracias a **TypeScript**
✅ Backend robusto con **FastAPI (Python)**
✅ **Streaming en tiempo real** usando Server-Sent Events
✅ Renderizado elegante con **Markdown + Tailwind Typography**
✅ Estilo profesional con **Glassmorphism y gradientes animados**
✅ Despliegue 100% en **Vercel**, escalable y seguro

---

# 📘 Lo que Has Aprendido

### 🧩 Estructura de una app full-stack moderna

Cómo conectar **Next.js (frontend)** con **FastAPI (backend)** de manera fluida.

### ⚛️ Client-side rendering con `"use client"`

* Los componentes marcados con `"use client"` se ejecutan **en el navegador**.
* Permiten usar *React hooks* (`useState`, `useEffect`).
* Perfectos para **UIs interactivas y reactividad en tiempo real**.
* En este proyecto, fueron esenciales para conectarse al backend de Python y manejar el *streaming*.

### 🔧 Creación de API endpoints en FastAPI

* Cómo devolver datos de OpenAI usando streaming con `StreamingResponse`.
* Cómo mantener el flujo estable para mostrar texto en vivo.

### 🪄 Renderizado Markdown en React

* Mostrar contenido estructurado (títulos, listas, negritas).
* Usar `react-markdown` junto con `remark-gfm` y `remark-breaks`.

### ☁️ Despliegue en Vercel

* Integración directa entre Next.js y Python.
* Variables de entorno seguras para claves API.
* Despliegue con un solo comando (`vercel --prod`).

---

# 🧭 Siguientes Pasos

Ahora que tienes la base sólida, puedes seguir ampliando tu SaaS:

* 🔁 **Añadir un botón** para generar nuevas ideas sin recargar la página.
* 💾 **Guardar ideas en una base de datos** (ej. Supabase o Firebase).
* 🔐 **Autenticación de usuarios** (con Clerk o Auth.js).
* 🧠 **Categorías de ideas** (negocios, educación, productividad, etc.).
* 📋 **Botón “Copiar al portapapeles”** para compartir resultados.
* ⭐ **Función para guardar o compartir ideas** en redes sociales.

---

# 🧰 Solución de Problemas Comunes

### ❌ “Module not found”

* Verifica que instalaste todos los paquetes con `npm install`.
* Si persiste, borra `node_modules` y ejecuta nuevamente `npm install`.

### 💤 La API no responde

* Asegúrate de haber agregado correctamente tu clave `OPENAI_API_KEY` en Vercel.
* Verifica que tengas crédito disponible en tu cuenta de OpenAI.

### 🌀 El *streaming* no funciona

* Algunos navegadores bloquean SSE en `localhost`. Prueba otro navegador o despliega en Vercel.
* Revisa la consola del navegador (F12 → pestaña **Console**) para errores.

### ⚠️ Advertencias de ESLint

* Líneas amarillas = advertencias (no bloquean la ejecución).
* Líneas rojas = errores (deben corregirse).
* Puedes desactivar una advertencia puntual con `// eslint-disable-next-line`.

### 🧩 Errores de TypeScript

* Instala los tipos con `npm install --save-dev @types/react @types/node`.
* Reinicia el servidor (`Ctrl+C` y luego `npm run dev`).

### 🚫 Problemas de despliegue

* Asegúrate de guardar todos los archivos antes de ejecutar `vercel`.
* Si usas `vercel.json`, revisa que el JSON esté correctamente formateado.
* Comprueba que tu variable `OPENAI_API_KEY` esté activa en Vercel.
