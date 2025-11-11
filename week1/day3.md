# Día 3: Añadir autenticación de usuarios con Clerk

## Transforma tu SaaS con autenticación profesional

Hoy añadirás autenticación de nivel empresarial a tu Generador de Ideas de Negocio, permitiendo que las personas inicien sesión con Google, GitHub y otros proveedores. Esto convierte tu app de un demo en un verdadero producto SaaS.

## Lo que construirás

Una versión autenticada de tu app que:
- Exige que las personas inicien sesión antes de acceder al generador de ideas
- Admite múltiples proveedores de autenticación (Google, GitHub, Email)
- Envía tokens JWT seguros a tu backend
- Verifica la identidad del usuario en cada petición a la API
- Funciona sin fricción con el Pages Router de Next.js

## Requisitos previos

- Haber completado el Día 2 (Generador de Ideas de Negocio funcionando)
- Tu proyecto desplegado en Vercel

## Nota IMPORTANTE - añadida después de los videos

En algunas situaciones, si tu app tarda más de 60 segundos en responder a una solicitud, es posible que veas un error de Timeout. En la consola de JavaScript del navegador aparecerá un error 403. El arreglo para esto está en community_contributions, explicado en el archivo jwt_token_60s_fix.md. Mantente atento a ese 403 tras 60 segundos y, si sucede, consulta la solución. ¡Gracias!

## Parte 1: Autenticación de usuarios

### Paso 1: Crea tu cuenta de Clerk

1. Visita [clerk.com](https://clerk.com) y haz clic en **Sign Up**
2. Crea tu cuenta usando Google (o el método que prefieras)
3. Se te llevará a **Create Application** (o haz clic en "Create Application" si regresas más tarde)

### Paso 2: Configura tu aplicación de Clerk

1. **Nombre de la aplicación:** SaaS
2. **Opciones de inicio de sesión:** habilita estos proveedores:
   - Email
   - Google  
   - GitHub
   - Apple (opcional)
3. Haz clic en **Create Application**

Verás el panel de Clerk con tus claves API.

### Paso 3: Instala las dependencias de Clerk

En tu terminal, instala el SDK de Clerk:

```bash
npm install @clerk/nextjs
```

Para manejar streaming con autenticación, instala también:

```bash
npm install @microsoft/fetch-event-source
```

### Paso 4: Configura las variables de entorno

Crea un archivo `.env.local` en la raíz de tu proyecto:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key_here
CLERK_SECRET_KEY=your_secret_key_here
```

**Importante:** copia estos valores desde el panel de Clerk (aparecen después de crear tu aplicación en la pantalla de configuración).

### Añade a .gitignore

Abre `.gitignore` en Cursor y añade `.env.local` en una nueva línea.

### Paso 5: Añade el proveedor de Clerk a tu app

Con Pages Router necesitamos envolver nuestra aplicación con el proveedor de Clerk. Actualiza `pages/_app.tsx`:

```typescript
import { ClerkProvider } from '@clerk/nextjs';
import type { AppProps } from 'next/app';
import '../styles/globals.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps}>
      <Component {...pageProps} />
    </ClerkProvider>
  );
}
```

### Paso 6: Crea la página del producto

Mueve tu generador de ideas a una ruta protegida. Como estamos usando autenticación en el cliente, protegeremos esa ruta con los componentes incorporados de Clerk.

Crea `pages/product.tsx`:

```typescript
"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useAuth } from '@clerk/nextjs';
import { fetchEventSource } from '@microsoft/fetch-event-source';

export default function Product() {
    const { getToken } = useAuth();
    const [idea, setIdea] = useState<string>('…loading');

    useEffect(() => {
        let buffer = '';
        (async () => {
            const jwt = await getToken();
            if (!jwt) {
                setIdea('Authentication required');
                return;
            }
            
            await fetchEventSource('/api', {
                headers: { Authorization: `Bearer ${jwt}` },
                onmessage(ev) {
                    buffer += ev.data;
                    setIdea(buffer);
                },
                onerror(err) {
                    console.error('SSE error:', err);
                    // Don't throw - let it retry
                }
            });
        })();
    }, []); // Empty dependency array - run once on mount

    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            <div className="container mx-auto px-4 py-12">
                {/* Header */}
                <header className="text-center mb-12">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                        Business Idea Generator
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                        AI-powered innovation at your fingertips
                    </p>
                </header>

                {/* Content Card */}
                <div className="max-w-3xl mx-auto">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
                        {idea === '…loading' ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="animate-pulse text-gray-400">
                                    Generating your business idea...
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

### Paso 7: Crea la landing page

Actualiza `pages/index.tsx` para que sea tu nueva landing con inicio de sesión:

```typescript
"use client"

import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            IdeaGen
          </h1>
          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-4">
                <Link 
                  href="/product" 
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-24">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Generate Your Next
            <br />
            Big Business Idea
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Harness the power of AI to discover innovative business opportunities tailored for the AI agent economy
          </p>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Get Started Free
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Generate Ideas Now
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </main>
  );
}
```

### Paso 8: Configura la autenticación del backend

Primero, obtén tu URL JWKS desde Clerk:
1. Ve a tu panel de Clerk
2. Haz clic en **Configure** (en la barra superior)
3. Haz clic en **API Keys** (en la barra lateral)  
4. Busca **JWKS URL** y cópiala

**¿Qué es JWKS?** La URL JWKS (JSON Web Key Set) es un endpoint público que contiene las claves públicas de Clerk. Cuando una persona inicia sesión, Clerk crea un JWT (JSON Web Token), un token firmado digitalmente que prueba la identidad del usuario. Tu backend en Python usa la URL JWKS para obtener las claves públicas de Clerk y verificar que los tokens JWT entrantes sean genuinos y no hayan sido manipulados. Esto permite una autenticación segura sin que tu backend tenga que contactar a Clerk en cada solicitud; puede verificar los tokens de forma independiente usando firmas criptográficas.

Añade a `.env.local`:
```bash
CLERK_JWKS_URL=your_jwks_url_here
```

### Paso 9: Actualiza las dependencias del backend

Añade la librería de autenticación de Clerk a `requirements.txt`:

```
fastapi
uvicorn
openai
fastapi-clerk-auth
```

### Paso 10: Actualiza la API con autenticación

Reemplaza `api/index.py` con:

```python
import os
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]  # User ID from JWT - available for future use
    # We now know which user is making the request! 
    # You could use user_id to:
    # - Track usage per user
    # - Store generated ideas in a database
    # - Apply user-specific limits or customization
    
    client = OpenAI()
    prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]
    stream = client.chat.completions.create(model="gpt-5-nano", messages=prompt, stream=True)

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### Paso 11: Añade las variables de entorno en Vercel

Añade tus claves de Clerk a Vercel:

```bash
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
```
Pega tu publishable key y selecciona todos los entornos.

```bash
vercel env add CLERK_SECRET_KEY
```
Pega tu secret key y selecciona todos los entornos.

```bash
vercel env add CLERK_JWKS_URL
```
Pega tu JWKS URL y selecciona todos los entornos.

### Paso 12: Prueba en local

Prueba tu autenticación en local:

```bash
vercel dev
```

**Nota:** el backend en Python no funcionará localmente con `vercel dev`, pero el flujo de autenticación sí funcionará perfecto. Podrás iniciar sesión, salir y ver la interfaz de usuario.

Visita `http://localhost:3000` y:
1. Haz clic en "Sign In"
2. Crea una cuenta o inicia sesión con Google/GitHub
3. Serás redirigido a la landing ya autenticada
4. Haz clic en "Go to App" para acceder al generador protegido

### Paso 13: Despliega a producción

Despliega tu app autenticada:

```bash
vercel --prod
```

Visita tu URL de producción y prueba todo el flujo de autenticación.

NOTA: si te aparece un problema con la expiración del token JWT, revisa este [arreglo aportado por Artur P](../community_contributions/arturp_jwt_token_fix_notes.md)

## ¿Qué está pasando?

Tu app ahora tiene:
- **Autenticación segura**: las personas deben iniciar sesión para usar tu producto
- **Protección de rutas en el cliente**: quienes no estén autenticados son redirigidos desde las páginas protegidas
- **Verificación de JWT**: cada petición a la API se verifica con firmas criptográficas
- **Identificación de usuarios**: el backend sabe quién hace cada solicitud
- **Experiencia profesional**: inicio de sesión modal, gestión de perfil y redirecciones fluidas
- **Múltiples proveedores**: cada usuario elige su método de inicio de sesión favorito

## Arquitectura de seguridad

Como usamos Next.js del lado del cliente con un backend en Python separado:

1. **Frontend (navegador)**: la persona inicia sesión con Clerk → recibe un token de sesión
2. **Protección del lado del cliente**: las rutas protegidas verifican el estado de autenticación y redirigen si es necesario
3. **Petición a la API**: el navegador envía el token JWT directamente al backend en Python con cada solicitud
4. **Verificación en el backend**: FastAPI verifica el JWT usando las claves públicas (JWKS) de Clerk
5. **Contexto del usuario**: el backend puede acceder al ID y metadatos del usuario a partir del token verificado

Esta arquitectura mantiene tu despliegue de Next.js simple (solo estático/cliente) y, aun así, conserva una autenticación segura para tu API.

## Resolución de problemas

### Errores "Unauthorized"
- Revisa que las tres variables de entorno estén configuradas correctamente en Vercel
- Asegúrate de que la URL JWKS esté bien copiada desde Clerk
- Verifica que hayas iniciado sesión antes de acceder a `/product`

### El modal de inicio de sesión no aparece
- Comprueba que `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` comience con `pk_`
- Asegúrate de haber envuelto tu app con `ClerkProvider`
- Borra caché y cookies del navegador

### La API no autentica
- Verifica que `CLERK_JWKS_URL` esté en tu entorno
- Revisa que `fastapi-clerk-auth` esté en requirements.txt
- Comprueba que el token JWT se envía en el encabezado Authorization

### Problemas en desarrollo local
- Asegúrate de que `.env.local` tenga las tres variables de Clerk
- Reinicia tu servidor de desarrollo tras añadir las variables
- Intenta limpiar la caché de Next.js: `rm -rf .next`

## Próximos pasos

¡Felicidades! Añadiste autenticación profesional a tu SaaS. En la Parte 2 añadiremos:
- Planes de suscripción con Stripe
- Límites de uso según el nivel de suscripción
- Procesamiento de pagos
- Portal de clientes para gestionar sus suscripciones

¡Tu app ahora es un producto SaaS real con autenticación segura de usuarios!
