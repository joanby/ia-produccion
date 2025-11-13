# ⚡ GRATIFICACIÓN INSTANTÁNEA – Parte 2

## 🤖 Añadiendo IA a tu aplicación en producción

Ahora vamos a mejorar tu aplicación en producción con la **API de OpenAI** para generar contenido dinámico con inteligencia artificial. 🧠✨

---

## 🪄 Paso 1: Obtén tu clave de API de OpenAI

Si aún no tienes una clave, sigue estos pasos:

1. Ve a 👉 [https://platform.openai.com](https://platform.openai.com) y crea una cuenta nueva.
2. Añade crédito a tu cuenta:

   * Entra en [https://platform.openai.com/settings/organization/billing/overview](https://platform.openai.com/settings/organization/billing/overview)
   * Realiza el pago mínimo de **$5 USD**
   * ⚠️ **Importante:** asegúrate de que **“Auto Recharge” esté DESACTIVADO**
3. Crea tu clave API:

   * Visita [https://platform.openai.com/settings/organization/api-keys](https://platform.openai.com/settings/organization/api-keys)
   * Haz clic en **“Create new secret key”**
   * Tu clave empezará con `sk-proj-...`
   * Cópiala al portapapeles y **guárdala en un lugar seguro** (usa un editor de texto plano, no Word o similares)

---

## 🔐 Paso 2: Añade tu clave API a Vercel

En la terminal de Cursor, escribe:

```bash
vercel env add OPENAI_API_KEY
```

* Cuando se te pida el valor, pega tu clave API
* Selecciona **todas las opciones** (development, preview, production) cuando se te pregunte

---

## ⚙️ Paso 3: Actualiza tus dependencias

Abre el archivo `requirements.txt` y añade la librería de OpenAI:

```
fastapi  
uvicorn  
openai
```

Guarda el archivo.

---

## 🧠 Paso 4: Actualiza el código de tu aplicación

Reemplaza **todo el contenido** de `instant.py` con el siguiente código:

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def instant():
    client = OpenAI()
    message = """
¡Estás en un sitio web que acaba de entrar en producción por primera vez!
Por favor, responde con un anuncio entusiasta para dar la bienvenida a los visitantes, explicando que el sitio está en producción por primera vez.
"""
    messages = [{"role": "user", "content": message}]
    response = client.chat.completions.create(model="gpt-5-nano", messages=messages)
    reply = response.choices[0].message.content.replace("\n", "<br/>")
    html = f"<html><head><title>¡En vivo al instante!</title></head><body><p>{reply}</p></body></html>"
    return html
```

💾 Guarda el archivo (`Ctrl + S` / `Cmd + S`).

---

## 🌐 Paso 5: Despliega tu app con IA

Primero, despliega en modo **desarrollo** para probar:

```bash
vercel .
```

Una vez desplegado:

1. Abre la URL proporcionada
2. Deberías ver un **mensaje de bienvenida generado por IA** 🎉
3. Actualiza la página para ver variaciones diferentes

Cuando todo funcione correctamente, despliega en **producción**:

```bash
vercel --prod
```

---

## ⚙️ ¿Qué está pasando detrás?

Tu aplicación ahora:

* 🔑 Se conecta a la API de OpenAI usando tu clave segura
* 💬 Genera mensajes únicos de bienvenida para cada visitante
* 🌍 Devuelve HTML formateado con el contenido generado por IA
* ☁️ Se ejecuta completamente *serverless* en la infraestructura de **Vercel**

---

## 🎉 ¡Felicidades!

Has logrado:

* ✅ Integrar inteligencia artificial en una aplicación en producción
* ✅ Proteger tus credenciales con variables de entorno
* ✅ Crear contenido dinámico y personalizado
* ✅ Construir tu **primera aplicación web impulsada por IA**

---

## 📘 Lo que has aprendido

* Cómo gestionar **claves API de forma segura** en producción
* Cómo integrar la **API de OpenAI** con **FastAPI**
* Cómo usar variables de entorno en **Vercel**
* Cómo generar **respuestas HTML dinámicas** con contenido IA

---

## 🚀 Próximos pasos

* Modifica el *prompt* para generar otros tipos de contenido
* Añade parámetros de consulta para personalizar la respuesta del modelo
* Experimenta con distintos modelos de OpenAI
* Agrega manejo de errores para fallos en la API

---

## 🧩 Solución de problemas

### ❌ “OpenAI API key not found”

* Asegúrate de haber ejecutado `vercel env add OPENAI_API_KEY`
* Comprueba que el nombre sea exactamente `OPENAI_API_KEY`
* Vuelve a desplegar después de añadir la variable

### ⚠️ “Insufficient credits”

* Revisa tu saldo en [https://platform.openai.com](https://platform.openai.com)
* Asegúrate de haber añadido al menos **$5 USD** de crédito

### 🕓 “La página carga lentamente”

* La primera petición puede tardar más por el *cold start*
* Las siguientes serán mucho más rápidas
* Este comportamiento es **normal en entornos serverless**

---

## 🔒 Nota de seguridad

Tu clave API está:

* 🔐 Nunca expuesta en el código
* 🧱 Almacenada de forma segura en las variables de entorno de Vercel
* 💻 Accesible **solo** desde tu aplicación desplegada
* 🚫 Invisible para el navegador o las herramientas de desarrollo

---

¿Quieres que te prepare la **traducción completa al español** del archivo `instant.py` con comentarios educativos (para incluir en un notebook del curso)?
