# 🚀 ¡GRATIFICACIÓN INSTANTÁNEA!

## 🧠 Despliegue en producción en minutos

Esta guía te mostrará cómo desplegar una aplicación sencilla de **FastAPI** en **Vercel** en menos de **10 minutos**. ⚡

---

## 🪄 Paso 1: Crea tu cuenta en Vercel

1. Abre tu navegador y entra en 👉 [https://vercel.com](https://vercel.com)
2. Haz clic en **Sign Up** (arriba a la derecha)
3. Selecciona el plan **Hobby** (para proyectos personales)
4. Escribe tu nombre
5. Elige un método para registrarte:

   * 💻 **GitHub** (recomendado) → “Continue with GitHub” y autoriza Vercel
   * 🧩 **GitLab** → “Continue with GitLab” y autoriza
   * 📦 **Bitbucket** → “Continue with Bitbucket” y autoriza
   * 📧 **Email** → Introduce tu correo y sigue los pasos de verificación
6. Completa el proceso de bienvenida (puedes omitir la creación de equipo)

---

## 💻 Paso 2: Instala el IDE **Cursor**

> 💡 Nota: puedes usar otro IDE como VS Code o PyCharm, pero estas instrucciones están pensadas para **Cursor**.

### 🪟 En Windows

1. Visita [https://cursor.com](https://cursor.com)
2. Haz clic en **Download for Windows**
3. Ejecuta el instalador `.exe` descargado
4. Sigue los pasos del asistente de instalación
5. Abre **Cursor** desde el menú Inicio o el escritorio

### 🍎 En Mac

1. Visita [https://cursor.com](https://cursor.com)
2. Haz clic en **Download for Mac**
3. Abre el archivo `.dmg` descargado
4. Arrastra **Cursor** a la carpeta **Applications**
5. Lanza la app desde **Applications** o con **Spotlight** (`Cmd + Space` → “Cursor”)

### 🐧 En Linux

1. Visita [https://cursor.com](https://cursor.com)
2. Haz clic en **Download for Linux**
3. Extrae el archivo `.tar.gz`:

   ```bash
   tar -xzf cursor-*.tar.gz
   ```
4. Muévelo a `/opt` y crea un enlace simbólico:

   ```bash
   sudo mv cursor /opt/
   sudo ln -s /opt/cursor/cursor /usr/local/bin/cursor
   ```
5. Ejecuta el comando `cursor` en la terminal para iniciarlo

---

### 📁 Crea tu carpeta de proyecto

1. Abre **Cursor**
2. **Windows/Linux:** Ve a *File → Open Folder →* crea una nueva carpeta llamada **instant**
3. **Mac:** *File → Open →* crea una carpeta llamada **instant**
4. Abre la carpeta **instant** en el IDE

---

## ⚙️ Paso 3: Crea tu aplicación **FastAPI**

En **Cursor**, crea un nuevo archivo llamado `instant.py` con el siguiente contenido:


```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def instant():
    return "Live from production!"
```
# ⚡ ¡DESPLIEGUE INSTANTÁNEO!

## 🚀 Despliegue en producción en minutos

Esta guía te mostrará cómo desplegar una aplicación **FastAPI** en **Vercel** en menos de **10 minutos**. 🧠✨

---

## 💾 Paso 4: Crea el archivo de dependencias

Crea un nuevo archivo llamado `requirements.txt` con el siguiente contenido:

```
fastapi
uvicorn
```

💡 **Guarda el archivo** (`Ctrl + S` en Windows/Linux, `Cmd + S` en Mac).

---

## ⚙️ Paso 5: Crea la configuración de Vercel

Crea un nuevo archivo llamado `vercel.json` con este contenido:

```json
{
    "builds": [
        {
            "src": "instant.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "instant.py"
        }
    ]
}
```

Guarda el archivo.

---

## 🟢 Paso 6: Instala Node.js

Vercel CLI requiere **Node.js**.

1. Ve a la página oficial de descargas: 👉 [https://nodejs.org/en/download](https://nodejs.org/en/download)
2. Elige tu método de instalación preferido:

   * 📦 **Descarga directa:** instala el ejecutable correspondiente a tu sistema operativo
   * 🍺 **Gestor de paquetes:** Homebrew (Mac), Chocolatey (Windows), apt/yum (Linux)
   * 🌀 **Gestor de versiones (recomendado):** nvm, fnm o volta para manejar versiones fácilmente
3. Una vez instalado, abre una **nueva terminal**
4. Verifica la instalación:

   ```bash
   node --version
   npm --version
   ```

   Si ambos comandos devuelven un número de versión, todo está correcto ✅

---

## 🌐 Paso 7: Despliega tu API en Vercel

### Abre la terminal en Cursor

* Ve a *Terminal → New Terminal* (o usa `Ctrl + \`` en Windows/Linux, `Cmd + `` en Mac)

💡 Asegúrate de estar dentro de tu carpeta de proyecto **instant**, y de que estén los tres archivos:
`instant.py`, `requirements.txt`, y `vercel.json`.

---

### 📦 Instala Vercel CLI y despliega

1. Instala la CLI de Vercel globalmente:

   ```bash
   npm install -g vercel
   ```

2. Inicia sesión en Vercel:

   ```bash
   vercel login
   ```

   * Introduce el correo con el que te registraste
   * Abre el enlace de verificación en tu email
   * Vuelve a la terminal: debería aparecer “Logged in as…”

3. Despliega tu aplicación (modo desarrollo):

   ```bash
   vercel .
   ```

   Durante la configuración:

   * “Set up and deploy?” → **Enter**
   * “Which scope?” → Selecciona tu cuenta personal
   * “Link to existing project?” → Escribe **n**
   * “What’s your project’s name?” → Escribe **instant**
   * “In which directory is your code located?” → **Enter**
     ⏳ Espera unos segundos (30–60s) hasta que se complete el despliegue
     Obtendrás una URL como:
     👉 `https://instant-xxxxxx.vercel.app`

4. Prueba tu API:
   Abre el enlace en tu navegador y deberías ver:
   **"Live from production!"** 🎉

---

## 🏁 ¡Felicidades! 🎉

Has desplegado tu primera API en producción. Tu API ahora está:

* ✅ En línea y accesible desde cualquier parte del mundo
* 🔒 Protegida con HTTPS
* ⚙️ Escalable automáticamente
* 💡 Sin necesidad de configurar servidores

---

## 🧭 Lo que has aprendido

* Cómo crear una aplicación básica con **FastAPI**
* Cómo preparar un proyecto para **Vercel**
* Cómo desplegar usando la **Vercel CLI**

---

## 🚀 Próximos pasos

* Cambia el mensaje en `instant.py` y vuelve a desplegar
* Añade nuevos endpoints a tu API
* Explora tu panel de control en 👉 [https://vercel.com/dashboard](https://vercel.com/dashboard)

---

## 🧩 Solución de problemas

### ❌ “vercel: command not found”

* Asegúrate de haber abierto una nueva terminal tras instalar Node.js
* Prueba a reinstalar la CLI:

  ```bash
  npm install -g vercel
  ```

### ⚠️ “Python version not supported”

* Vercel soporta Python **3.9, 3.10, 3.11 y 3.12**
* Si da error, añade un archivo `runtime.txt` con:

  ```
  python-3.12
  ```

### ❗ Error en el despliegue

* Verifica que los tres archivos (`instant.py`, `requirements.txt`, `vercel.json`) estén en el mismo directorio
* Comprueba que estás ejecutando `vercel` dentro de esa carpeta
* Asegúrate de que tu `vercel.json` esté exactamente igual que el mostrado

---

### 🆘 ¿Necesitas ayuda?

* Consulta la documentación oficial de Vercel:
  👉 [https://vercel.com/docs](https://vercel.com/docs)
* Pregunta en clase o en el foro del curso 💬