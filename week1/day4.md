# Día 4: Asistente de Consultas Médicas

## Construye una aplicación sanitaria profesional

Hoy transformarás tu SaaS en un asistente de consultas médicas que ayude a los doctores a generar resúmenes de pacientes, acciones siguientes y correos amigables a partir de sus notas de visita.

## Lo que construirás

Una aplicación sanitaria que:
- Recibe como entrada las notas de la consulta del médico
- Genera resúmenes profesionales para el expediente
- Crea próximos pasos accionables para el doctor
- Redacta correos claros y comprensibles para el paciente
- Usa formularios estructurados con selectores de fecha
- Transmite contenido generado por IA en tiempo real

## Requisitos previos

- Haber completado el Día 3 (autenticación y suscripciones funcionando)
- Tu app desplegada en Vercel

## Paso 1: Instala dependencias adicionales

Necesitamos un selector de fecha para el formulario de consulta:

```bash
npm install react-datepicker
npm install --save-dev @types/react-datepicker
```

## Paso 2: Actualiza la API del backend

Reemplaza `api/index.py` con un nuevo endpoint que maneje los datos de la consulta:

```python
import os
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str


system_prompt = """
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
"""


def user_prompt_for(visit: Visit) -> str:
    return f"""Create the summary, next steps and draft email for:
Patient Name: {visit.patient_name}
Date of Visit: {visit.date_of_visit}
Notes:
{visit.notes}"""


@app.post("/api")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    user_id = creds.decoded["sub"]  # Available for tracking/auditing
    client = OpenAI()

    user_prompt = user_prompt_for(visit)

    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=prompt,
        stream=True,
    )

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

Observa los cambios clave:
- Cambiamos de `@app.get("/api")` a `@app.post("/api")` para aceptar datos del formulario
- Añadimos un modelo `Visit` para validar la entrada
- Estructuramos los prompts para producir salida específica del ámbito sanitario

## Paso 3: Actualiza la configuración de la aplicación

Primero, importa los estilos del date picker en `pages/_app.tsx`:

```typescript
import { ClerkProvider } from '@clerk/nextjs';
import type { AppProps } from 'next/app';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/globals.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps}>
      <Component {...pageProps} />
    </ClerkProvider>
  );
}
```

Ahora actualiza `pages/_document.tsx` para reflejar el enfoque sanitario:

```typescript
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <title>Healthcare Consultation Assistant</title>
        <meta name="description" content="AI-powered medical consultation summaries" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
```

## Paso 4: Crea el formulario de consulta

Reemplaza `pages/product.tsx` con la nueva interfaz sanitaria:

```typescript
"use client"

import { useState, FormEvent } from 'react';
import { useAuth } from '@clerk/nextjs';
import DatePicker from 'react-datepicker';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { Protect, PricingTable, UserButton } from '@clerk/nextjs';

function ConsultationForm() {
    const { getToken } = useAuth();

    // Form state
    const [patientName, setPatientName] = useState('');
    const [visitDate, setVisitDate] = useState<Date | null>(new Date());
    const [notes, setNotes] = useState('');

    // Streaming state
    const [output, setOutput] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setOutput('');
        setLoading(true);

        const jwt = await getToken();
        if (!jwt) {
            setOutput('Authentication required');
            setLoading(false);
            return;
        }

        const controller = new AbortController();
        let buffer = '';

        await fetchEventSource('/api', {
            signal: controller.signal,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({
                patient_name: patientName,
                date_of_visit: visitDate?.toISOString().slice(0, 10),
                notes,
            }),
            onmessage(ev) {
                buffer += ev.data;
                setOutput(buffer);
            },
            onclose() { 
                setLoading(false); 
            },
            onerror(err) {
                console.error('SSE error:', err);
                controller.abort();
                setLoading(false);
            },
        });
    }

    return (
        <div className="container mx-auto px-4 py-12 max-w-3xl">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-8">
                Consultation Notes
            </h1>

            <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
                <div className="space-y-2">
                    <label htmlFor="patient" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Patient Name
                    </label>
                    <input
                        id="patient"
                        type="text"
                        required
                        value={patientName}
                        onChange={(e) => setPatientName(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="Enter patient's full name"
                    />
                </div>

                <div className="space-y-2">
                    <label htmlFor="date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Date of Visit
                    </label>
                    <DatePicker
                        id="date"
                        selected={visitDate}
                        onChange={(d: Date | null) => setVisitDate(d)}
                        dateFormat="yyyy-MM-dd"
                        placeholderText="Select date"
                        required
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                </div>

                <div className="space-y-2">
                    <label htmlFor="notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Consultation Notes
                    </label>
                    <textarea
                        id="notes"
                        required
                        rows={8}
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="Enter detailed consultation notes..."
                    />
                </div>

                <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
                >
                    {loading ? 'Generating Summary...' : 'Generate Summary'}
                </button>
            </form>

            {output && (
                <section className="mt-8 bg-gray-50 dark:bg-gray-800 rounded-xl shadow-lg p-8">
                    <div className="markdown-content prose prose-blue dark:prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                            {output}
                        </ReactMarkdown>
                    </div>
                </section>
            )}
        </div>
    );
}

export default function Product() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            {/* User Menu in Top Right */}
            <div className="absolute top-4 right-4">
                <UserButton showName={true} />
            </div>

            {/* Subscription Protection */}
            <Protect
                plan="premium_subscription"
                fallback={
                    <div className="container mx-auto px-4 py-12">
                        <header className="text-center mb-12">
                            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                                Healthcare Professional Plan
                            </h1>
                            <p className="text-gray-600 dark:text-gray-400 text-lg mb-8">
                                Streamline your patient consultations with AI-powered summaries
                            </p>
                        </header>
                        <div className="max-w-4xl mx-auto">
                            <PricingTable />
                        </div>
                    </div>
                }
            >
                <ConsultationForm />
            </Protect>
        </main>
    );
}
```

## Paso 5: Actualiza la landing page

Actualiza `pages/index.tsx` para reflejar el enfoque sanitario:

```typescript
"use client"

import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            MediNotes Pro
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
                <UserButton showName={true} />
              </div>
            </SignedIn>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-16">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Transform Your
            <br />
            Consultation Notes
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            AI-powered assistant that generates professional summaries, action items, and patient communications from your consultation notes
          </p>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 backdrop-blur-sm">
                <div className="text-3xl mb-4">📋</div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Professional Summaries</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Generate comprehensive medical record summaries from your notes
                </p>
              </div>
            </div>
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-green-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 backdrop-blur-sm">
                <div className="text-3xl mb-4">✅</div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Action Items</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Clear next steps and follow-up actions for every consultation
                </p>
              </div>
            </div>
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 backdrop-blur-sm">
                <div className="text-3xl mb-4">📧</div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Patient Emails</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Draft clear, patient-friendly email communications automatically
                </p>
              </div>
            </div>
          </div>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Start Free Trial
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Access Premium Features
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </main>
  );
}
```

## Paso 6: Actualiza el backend para la nueva experiencia

Asegúrate de que tu archivo `api/index.py` esté desplegado en Vercel (ver Paso 2). Ejecuta:

```bash
vercel --prod
```

## Paso 7: Despliega la nueva interfaz

Actualiza tu aplicación en Vercel para poner en producción la UI centrada en salud:

```bash
vercel --prod
```

## Paso 8: Prueba el flujo de consultas

1. Visita tu URL de producción
2. Inicia sesión con tu cuenta
3. Navega al formulario de consulta
4. Prueba ingresando notas de ejemplo:

**Ejemplo de entrada:**
- **Patient Name:** Jane Smith
- **Date:** Fecha de hoy
- **Notes:** 
  ```
  Patient presents with persistent cough for 2 weeks. No fever. 
  Chest clear on examination. Blood pressure 120/80. 
  Likely viral bronchitis. Prescribed rest and fluids. 
  Follow up if symptoms persist beyond another week.
  ```

Recibirás:
1. Un resumen profesional para el expediente
2. Próximos pasos claros para el médico
3. Un borrador de correo comprensible para el paciente

## ¿Qué está pasando?

Tu app sanitaria ahora:
- **Acepta entrada estructurada**: formulario con nombre del paciente, fecha y notas
- **Valida los datos**: modelos Pydantic en el backend
- **Genera salida formateada**: tres secciones distintas para diferentes usos
- **Mantiene la seguridad**: todos los datos se envían con autenticación JWT
- **Soporta suscripciones**: solo las personas premium acceden a la herramienta

## Cambios de arquitectura respecto al Día 3

1. **POST en vez de GET**: la API ahora recibe datos del formulario vía POST
2. **Prompts estructurados**: el system prompt y user prompt guían el formato de salida
3. **Validación del formulario**: validación en frontend (campos requeridos) y backend (Pydantic)
4. **Manejo de fechas**: selector con formato ISO
5. **UI profesional**: diseño con foco sanitario y secciones claras

## Consideraciones de seguridad

**Importante:** Esta es una aplicación demostrativa. Para uso sanitario en producción:
- Implementa medidas completas de cumplimiento HIPAA
- Añade cifrado de datos en reposo y en tránsito
- Implementa registros de auditoría para todos los accesos
- Añade control de acceso basado en roles (doctor vs. admin)
- Define políticas adecuadas de retención de datos
- Gestiona el consentimiento del paciente

## Resolución de problemas

### Error "Method not allowed"
- Asegúrate de que el endpoint use `@app.post("/api")` y no `@app.get("/api")`
- Verifica que la petición fetch tenga `method: 'POST'`

### El date picker no se estiliza correctamente
- Confirma que `react-datepicker/dist/react-datepicker.css` se importe en `pages/_app.tsx`
- Comprueba que el date picker tenga la clase de Tailwind adecuada

### Los datos del formulario no se envían
- Revisa la consola del navegador en busca de errores
- Verifica que todos los campos requeridos tengan valores
- Asegúrate de que se obtenga correctamente el token JWT

### La salida no se formatea bien
- Asegura que los estilos de `markdown-content` sigan presentes (del Día 2)
- Verifica que los plugins de ReactMarkdown estén importados

## Ideas de personalización

### Añadir más campos
```typescript
// Añadir selección de especialidad
const [specialty, setSpecialty] = useState('General Practice');

// Añadir nivel de urgencia
const [urgency, setUrgency] = useState<'routine' | 'urgent' | 'emergency'>('routine');
```

### Plantillas mejoradas
Crea distintos prompts según la especialidad:
```python
def get_system_prompt(specialty: str) -> str:
    prompts = {
        "cardiology": "Focus on cardiac symptoms and cardiovascular health...",
        "pediatrics": "Use child-friendly language in patient communications...",
        "psychiatry": "Include mental health considerations and resources..."
    }
    return prompts.get(specialty, system_prompt)
```

### Opciones de exportación
Añade botones para exportar el contenido generado:
```typescript
const handleExportPDF = () => {
    // Generate PDF from markdown
};

const handleCopyEmail = () => {
    // Copy email section to clipboard
};
```

## Próximos pasos

¡Felicidades! Construiste un asistente profesional de consultas médicas con:
- ✅ Entrada estructurada de datos clínicos
- ✅ Generación de contenido impulsada por IA
- ✅ Salidas profesionales y orientadas al paciente
- ✅ Autenticación segura y suscripciones
- ✅ UI moderna y accesible

### Posibles mejoras

1. **Biblioteca de plantillas**: plantillas prediseñadas para condiciones comunes
2. **Entrada por voz**: soporte de dictado para las notas
3. **Multilenguaje**: correos al paciente en distintos idiomas
4. **Integraciones**: conexión con sistemas EHR
5. **Analítica**: seguimiento de patrones de consulta y tiempo ahorrado
6. **Colaboración**: permitir que varios doctores compartan plantillas

¡Tu asistente sanitario está listo para ayudar a profesionales médicos a ahorrar tiempo y mejorar la comunicación con sus pacientes!
