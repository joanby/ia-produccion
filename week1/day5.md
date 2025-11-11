# Día 5: Despliega tu SaaS en AWS App Runner

## De Vercel a AWS: despliegue profesional en la nube

Hoy llevarás tu Asistente de Consultas Médicas desde Vercel a AWS usando contenedores Docker y App Runner. Así es como los equipos profesionales despliegan aplicaciones de producción a escala.

## Lo que aprenderás

- **Contenerización con Docker** para despliegues consistentes
- **Fundamentos de AWS** y configuración de la cuenta
- **AWS App Runner** para alojar contenedores serverless
- **Patrones de despliegue en producción** usados por equipos de ingeniería
- **Monitoreo de costos** para mantener bajo control tu factura de AWS

## Importante: ¡protege tu presupuesto primero! 💰

AWS cobra por los recursos que utilizas. Configuremos alertas de costos ANTES de desplegar nada.

**Costos esperados**: con nuestra configuración, calcula ~$5-10/mes. AWS ofrece créditos del free tier para cuentas nuevas que suelen cubrir los primeros 3 meses.

Crearemos alertas de presupuesto en $1, $5 y $10 para vigilar el gasto. ¡Es una práctica profesional clave!

## Comprende los servicios de AWS que usaremos

Antes de comenzar, revisemos los servicios involucrados:

### AWS App Runner
**App Runner** es la forma más simple de AWS para desplegar aplicaciones web contenerizadas. Piensa en él como “Vercel para contenedores Docker”: maneja certificados HTTPS, balanceo y escalado automáticamente. Tú proporcionas el contenedor y App Runner hace el resto.

### Amazon ECR (Elastic Container Registry)
**ECR** es como GitHub pero para imágenes Docker. Allí almacenaremos la aplicación contenerizada antes de desplegarla en App Runner.

### AWS IAM (Identity and Access Management)
**IAM** controla quién puede acceder a qué dentro de tu cuenta de AWS. Crearemos un usuario especial con permisos limitados por seguridad: ¡nunca uses tu cuenta root para el trabajo diario!

### CloudWatch
**CloudWatch** es el servicio de monitoreo de AWS. Recoge logs de tu aplicación y ayuda a depurar problemas; es como tener la consola del navegador para tu servidor.

## Parte 1: Crea tu cuenta de AWS

## ESPERA – ¡AVISO IMPORTANTE DESCUBIERTO TRAS PUBLICAR!

Existe una opción para quienes usan AWS por primera vez que permite seleccionar el “free tier”. ¡No la elijas! Tiene acceso limitado a los servicios, incluido que no permite App Runner (el servicio que usamos hoy). Esto no significa pagar suscripciones o soporte; solo que debes introducir datos de pago y no estar en un entorno sandbox. El estudiante Jake C. confirmó que los $120 de créditos gratuitos siguen aplicando incluso tras registrarse con una cuenta completa.

Esto lo descubrió brillantemente el estudiante Andy C., quien compartió:

> **Mensaje críptico de App Runner: "The AWS Access Key Id needs a subscription for the service"**  
> Luché con este mensaje durante 24 horas y quería que todos supieran la causa raíz. Me aparecía cuando (1) intentaba crear una configuración de "Auto scaling" (por ejemplo, "Basic", como sugiere Ed) y (2) cuando trataba de guardar y crear mi servicio de App Runner.  
>  
> El problema fue: estaba registrado en el free tier de AWS. Aparentemente el free tier no permite usar App Runner. Una vez que actualicé a la cuenta de pago, todo funcionó.  
>  
> Probé muchas otras cosas e invertí horas intentando entender IAM, pensando que ese era el problema. ¡Espero que este mensaje le ahorre a alguien una enorme cantidad de tiempo!

Este es un ejemplo de los horrores de infraestructura que podrías enfrentar; enorme agradecimiento a Andy por investigar, hallar la causa y compartirla.

Con eso en mente:

### Paso 1: Regístrate en AWS

1. Visita [aws.amazon.com](https://aws.amazon.com)
2. Haz clic en **Create an AWS Account**
3. Ingresa tu correo y elige una contraseña
4. Selecciona el tipo de cuenta **Personal** (para aprendizaje)
5. Introduce la información de pago (obligatoria, pero configuraremos alertas)
6. Verifica tu teléfono vía SMS
7. Selecciona **Basic Support - Free**

Ahora tienes una cuenta root en AWS. Es como tener acceso de administrador: poderoso, pero peligroso.

### Paso 2: Asegura tu cuenta root

1. Inicia sesión en la consola de AWS
2. Haz clic en tu nombre de cuenta (arriba a la derecha) → **Security credentials**
3. Activa **Multi-Factor Authentication (MFA)**:
   - Haz clic en **Assign MFA device**
   - Nombre: `root-mfa`
   - Selecciona **Authenticator app**
   - Escanea el código QR con Google Authenticator o Authy
   - Introduce dos códigos consecutivos
   - Haz clic en **Add MFA**

### Paso 3: Configura alertas de presupuesto (¡crítico!)

1. En la consola de AWS, busca **Billing** y abre **Billing and Cost Management**
2. En el menú izquierdo, haz clic en **Budgets**
3. Pulsa **Create budget**
4. Selecciona **Use a template (simplified)**
5. Elige **Monthly cost budget**
6. Configura tres presupuestos:

**Presupuesto 1 – Alerta temprana ($1)**:
- Nombre: `early-warning`
- Monto: `1` USD
- Emails: tu dirección
- Pulsa **Create budget**

**Presupuesto 2 – Precaución ($5)**:
- Repite los pasos
- Nombre: `caution-budget`
- Monto: `5` USD
- Emails: tu correo
- Crear presupuesto

**Presupuesto 3 – Detente ($10)**:
- Repite el proceso
- Nombre: `stop-budget`
- Monto: `10` USD
- Emails: tu correo
- Crear presupuesto

AWS te notificará automáticamente cuando:
- El gasto real llegue al 85% del presupuesto
- El gasto real alcance el 100%
- El gasto proyectado vaya camino al 100%

Si llegas a $10, detente y revisa qué está en ejecución.

### Paso 4: Crea un usuario IAM para el trabajo diario

Nunca uses la cuenta root para tareas diarias. Crearemos un usuario limitado:

1. Busca **IAM** en la consola
2. Haz clic en **Users** → **Create user**
3. Username: `aiengineer`
4. Marca ✅ **Provide user access to the AWS Management Console**
5. Selecciona **I want to create an IAM user**
6. Elige **Custom password** y define una contraseña fuerte
7. Desmarca ⬜ **Users must create a new password at next sign-in**
8. Haz clic en **Next**

### Paso 5: Crea un grupo con permisos

Primero crearemos un grupo reutilizable y luego añadiremos al usuario:

1. En la página de permisos, elige **Add user to group**
2. Pulsa **Create group**
3. Nombre: `BroadAIEngineerAccess`
4. En el buscador de políticas, marca:
   - `AWSAppRunnerFullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `CloudWatchLogsFullAccess`
   - `IAMUserChangePassword`
   - IMPORTANTE: también `IAMFullAccess` (no aparece en el video, pero es necesario o tendrás errores más adelante; gracias Anthony W y Jake C por avisar)
5. Haz clic en **Create user group**
6. De vuelta en permisos, selecciona el grupo `BroadAIEngineerAccess`
7. Pulsa **Next** → **Create user**
8. **Importante**: haz clic en **Download .csv file** y guárdalo en un lugar seguro.

Ten presente que podrías recibir errores de permisos cuando AWS indique que tu usuario no tiene acceso a algo. La solución suele ser volver a esta pantalla (como usuario root) y adjuntar otra política. Es una tarea muy común cuando trabajas con AWS…

### Paso 6: Inicia sesión como usuario IAM

1. Cierra sesión de la cuenta root
2. Ve a tu URL de inicio de sesión (aparece en el CSV, algo como `https://123456789012.signin.aws.amazon.com/console`)
3. Inicia sesión con:
   - Usuario: `aiengineer`
   - Contraseña: la que definiste

✅ **Punto de control**: Debes ver “aiengineer @ Account-ID” arriba a la derecha

## Parte 2: Instala Docker Desktop

Docker nos permite empaquetar la aplicación en un contenedor, como un contenedor marítimo para software.

### Paso 1: Instala Docker Desktop

1. Visita [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Descarga según tu sistema:
   - **Mac**: versión para Apple Silicon o Intel
   - **Windows**: requiere Windows 10/11
3. Ejecuta el instalador
4. **Windows**: Docker instalará WSL2 si hace falta; acepta los avisos
5. Abre Docker Desktop
6. Puede que debas reiniciar tu equipo

### Paso 2: Verifica que Docker funcione

Abre Terminal (Mac) o PowerShell (Windows):

```bash
docker --version
```

Deberías ver algo como `Docker version 26.x.x`

Prueba Docker:
```bash
docker run hello-world
```

Deberías ver “Hello from Docker!” confirmando que funciona correctamente.

✅ **Punto de control**: El ícono de Docker Desktop (ballena) debe estar activo.

## Parte 3: Prepara tu aplicación

Necesitamos adaptar la app del Día 4 para AWS. El cambio clave: exportaremos Next.js como archivos estáticos y serviremos todo desde un solo contenedor.

### Paso 1: Revisa la estructura del proyecto

Debe lucir así:
```
saas/
├── pages/
├── styles/
├── api/
├── public/
├── node_modules/
├── .env.local
├── .gitignore
├── package.json
├── requirements.txt
├── next.config.ts
└── tsconfig.json
```

### Paso 2: Convierte a exportación estática

**Cambio arquitectónico importante**: en Vercel, Next.js podía hacer solicitudes del lado del servidor. Para simplificar en AWS, exportaremos Next.js como archivos HTML/JS estáticos y los serviremos desde el backend Python. ¡Todo vivirá en un único contenedor!

**Nota sobre middleware**: con Pages Router no usamos archivos de middleware. La autenticación la manejan completamente los componentes client-side de Clerk (`<Protect>`, `<SignedIn>`, etc.), que funcionan perfecto con export estático.

Actualiza `next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',  // Esto genera archivos estáticos
  images: {
    unoptimized: true  // Requerido para export estático
  }
};

export default nextConfig;
```

### Paso 3: Actualiza las llamadas del frontend a la API

Como frontend y backend vivirán en el mismo dominio, ajusta la llamada:

```typescript
// Antes (Vercel)
await fetchEventSource('/api', {

// Nuevo (AWS)
await fetchEventSource('/api/consultation', {
```

Esto funciona porque ambos servicios se servirán desde el mismo contenedor.

### Paso 4: Actualiza el servidor backend

Crea `api/server.py`, que alojará tanto la API como los archivos estáticos:

```python
import os
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/api/consultation")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    user_id = creds.decoded["sub"]
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

@app.get("/health")
def health_check():
    return {"status": "healthy"}

static_path = Path("static")
if static_path.exists():
    @app.get("/")
    async def serve_root():
        return FileResponse(static_path / "index.html")

    app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### Paso 5: Crea el archivo de entorno para AWS

Genera `.env` (copia de `.env.local` pero añade datos de AWS):

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_JWKS_URL=https://...
OPENAI_API_KEY=sk-...

DEFAULT_AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
```

Para encontrar tu Account ID: en la consola, haz clic en tu usuario (arriba a la derecha) y copia el número de 12 dígitos.

**Importante**: añade `.env` a `.gitignore` si aún no está.

## Parte 4: Configura Docker

Docker nos permitirá empaquetar todo en un contenedor.

### Paso 1: Crea el Dockerfile

```dockerfile
# Etapa 1: construir los archivos estáticos de Next.js
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Copiamos los archivos de dependencias primero (mejor caché)
COPY package*.json ./
RUN npm ci

# Copiamos el resto del frontend
COPY . .

# Pasamos la publishable key al build (es pública por diseño)
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

# Generamos la exportación estática (carpeta out)
RUN npm run build

# Etapa 2: contenedor final de Python
FROM python:3.12-slim

WORKDIR /app

# Dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Servidor FastAPI
COPY api/server.py .

# Archivos estáticos generados por Next.js
COPY --from=frontend-builder /app/out ./static

# Health check para App Runner
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# FastAPI escuchará en el puerto 8000
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Paso 2: Crea `.dockerignore`

```
node_modules
.next
.env
.env.local
.git
.gitignore
README.md
.DS_Store
*.log
.vercel
dist
build
```

## Parte 5: Construye y prueba en local

Probemos el contenedor antes de ir a AWS.

### Paso 1: Carga las variables de entorno

**Mac/Linux**:
```bash
export $(cat .env | grep -v '^#' | xargs)
```

**Windows (PowerShell)**:
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^(.+?)=(.+)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}
```

### Paso 2: Construye la imagen Docker

**Mac/Linux**:
```bash
docker build   --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"   -t consultation-app .
```

**Windows PowerShell**:
```powershell
docker build `
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$env:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" `
  -t consultation-app .
```

La primera vez toma 2-3 minutos.

### Paso 3: Ejecuta localmente

**Mac/Linux**:
```bash
docker run -p 8000:8000   -e CLERK_SECRET_KEY="$CLERK_SECRET_KEY"   -e CLERK_JWKS_URL="$CLERK_JWKS_URL"   -e OPENAI_API_KEY="$OPENAI_API_KEY"   consultation-app
```

**Windows PowerShell**:
```powershell
docker run -p 8000:8000 `
  -e CLERK_SECRET_KEY="$env:CLERK_SECRET_KEY" `
  -e CLERK_JWKS_URL="$env:CLERK_JWKS_URL" `
  -e OPENAI_API_KEY="$env:OPENAI_API_KEY" `
  consultation-app
```

### Paso 4: Prueba la aplicación

1. Abre `http://localhost:8000`
2. Inicia sesión con Clerk
3. Completa el formulario de consulta
4. Verifica que todo funcione

Para detener: `Ctrl+C`

✅ **Punto de control**: La app se comporta igual que en Vercel

## Parte 6: Despliega en AWS

### Paso 1: Crea un repositorio ECR

1. En la consola, busca **ECR**
2. Haz clic en **Create repository**
3. Verifica que estés en la región correcta
4. Configuración:
   - Visibilidad: **Private**
   - Nombre: `consultation-app`
   - Resto por defecto
5. Crea el repositorio y verifica que aparezca

### Paso 2: Configura AWS CLI

#### Crea claves de acceso

1. En IAM → Users → `aiengineer`
2. Abre la pestaña **Security credentials**
3. En **Access keys**, pulsa **Create access key**
4. Selecciona **Command Line Interface (CLI)**
5. Marca la casilla de confirmación → **Next**
6. Descripción: `Docker push access`
7. Haz clic en **Create access key**
8. **Crucial**: descarga el CSV o copia ambos valores
9. Pulsa **Done**

#### Configura AWS CLI

Instala AWS CLI si hace falta y ejecuta:
```bash
aws configure
```

Introduce:
- AWS Access Key ID: (pega tu clave)
- AWS Secret Access Key: (pega tu secreto)
- Región por defecto (elige la más cercana)
- Formato por defecto: `json`

### Paso 3: Envía la imagen a ECR

Asegúrate de tener tus variables (`.env`) cargadas.

**Mac/Linux**:
```bash
# 1. Autentica Docker contra ECR
aws ecr get-login-password --region $DEFAULT_AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com

# 2. Construye para Linux/AMD64 (CRÍTICO en Mac Apple Silicon)
docker build   --platform linux/amd64   --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"   -t consultation-app .

# 3. Etiqueta la imagen para tu repositorio
docker tag consultation-app:latest $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest

# 4. Haz push a ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest
```

**Windows PowerShell**:
```powershell
# 1. Autentica Docker contra ECR
aws ecr get-login-password --region $env:DEFAULT_AWS_REGION | docker login --username AWS --password-stdin "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:DEFAULT_AWS_REGION.amazonaws.com"

# 2. Construye para Linux/AMD64
docker build `
  --platform linux/amd64 `
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$env:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" `
  -t consultation-app .

# 3. Etiqueta la imagen
docker tag consultation-app:latest "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest"

# 4. Haz push a ECR
docker push "$env:AWS_ACCOUNT_ID.dkr.ecr.$env:DEFAULT_AWS_REGION.amazonaws.com/consultation-app:latest"
```

El push tardará 2-5 minutos. Verifica en ECR que exista la imagen `latest`.

✅ **Punto de control**: Debes ver la imagen en ECR

## Parte 7: Crea el servicio de App Runner

### Paso 1: Inicia App Runner

1. Busca **App Runner** en la consola
2. Haz clic en **Create service**

### Paso 2: Configura la fuente

1. Repository type: **Container registry**
2. Provider: **Amazon ECR**
3. Selecciona `consultation-app` → etiqueta `latest`
4. Deployment trigger: **Manual**
5. ECR access role: **Create new service role**
6. Pulsa **Next**

### Paso 3: Configura el servicio

1. **Service name**: `consultation-app-service`
2. **vCPU y memoria**: 0.25 vCPU / 0.5 GB
3. **Environment variables**:
   - `CLERK_SECRET_KEY`
   - `CLERK_JWKS_URL`
   - `OPENAI_API_KEY`
4. **Port**: `8000`
5. **Auto scaling**: mínimo 1, máximo 1 (para controlar costos)
6. Pulsa **Next**

### Paso 4: Configura el health check

1. Protocolo: HTTP
2. Path: `/health`
3. Intervalo: 20 s
4. Timeout: 5 s
5. Healthy threshold: 2
6. Unhealthy threshold: 5

Pulsa **Next**

### Paso 5: Revisa y crea

1. Revisa todos los ajustes
2. Haz clic en **Create & deploy**
3. Espera 5-10 minutos
4. El estado pasará a “Running”

✅ **Punto de control**: Servicio con check verde

### Paso 6: Accede a la aplicación

1. Haz clic en el **Default domain** (ej. `abc123.us-east-1.awsapprunner.com`)
2. La app debería cargar con HTTPS automático
3. Prueba todo: iniciar sesión, generar resumen, cerrar sesión

🎉 ¡Tu app sanitaria ya corre en AWS!

## Parte 8: Monitoreo y depuración

### Ver logs

1. En tu servicio App Runner, abre la pestaña **Logs**
2. **Application logs**: salida de tu app
3. **System logs**: logs de despliegue/infraestructura
4. Haz clic en **View in CloudWatch** para más detalle

### Problemas comunes y soluciones

**Estado “Unhealthy”**:
- Revisa los logs de la aplicación por errores de Python
- Verifica variables de entorno
- Asegura que el health check use `/health`

**“Authentication failed”**:
- Revisa las variables de Clerk
- Confirma que la JWKS URL sea correcta
- Consulta los logs en CloudWatch

**La página no carga**:
- Verifica que el puerto sea 8000
- Confirma que la imagen se construyó con `--platform linux/amd64`
- Asegura que los archivos estáticos se sirvan correctamente

## Parte 9: Actualiza tu aplicación

Cuando realices cambios:

### Paso 1: Recompila y publica

**Mac/Linux**:
```bash
# 1. Recompila con el flag de plataforma
docker build   --platform linux/amd64   --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"   -t consultation-app .

# 2. Etiqueta para ECR
docker tag consultation-app:latest YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com/consultation-app:latest

# 3. Haz push a ECR
docker push YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com/consultation-app:latest
```

**Windows PowerShell**:
```powershell
# 1. Recompila con el flag de plataforma
docker build `
  --platform linux/amd64 `
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$env:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" `
  -t consultation-app .

# 2. Etiqueta para ECR
docker tag consultation-app:latest YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com/consultation-app:latest

# 3. Haz push a ECR
docker push YOUR-ACCOUNT-ID.dkr.ecr.YOUR-REGION.amazonaws.com/consultation-app:latest
```

### Paso 2: Despliega la actualización

1. Ve a la consola de App Runner
2. Haz clic en tu servicio
3. Pulsa **Deploy**
4. Espera a que finalice el despliegue

## Gestión de costos

### ¿Cuánto cuesta?

Con nuestra configuración mínima (1 instancia siempre activa):
- App Runner: ~$0.007/h ≈ ~$5/mes
- ECR: ~$0.10/GB/mes
- Total: ~$5-6/mes

App Runner requiere al menos 1 instancia corriendo, así que pagarás disponibilidad continua. Para ahorrar, pausa el servicio cuando no lo uses.

### Cómo ahorrar dinero

1. **Pausa cuando no lo uses**: Actions → **Pause service**
2. **Aprovecha el free tier**: las cuentas nuevas reciben créditos
3. **Monitorea los presupuestos**: revisa tu email
4. **Limpia ECR**: elimina imágenes antiguas

### Control de costos de emergencia

Si recibes alertas:
1. Ve a App Runner → Actions → **Pause service**
2. Revisa los logs en CloudWatch
3. Verifica en ECR si hay múltiples versiones (borra las viejas)

## Lo que has logrado

Has conseguido:
- ✅ Crear una cuenta AWS segura siguiendo buenas prácticas
- ✅ Contenerizar una app full-stack con Docker
- ✅ Desplegar en AWS App Runner con HTTPS y monitoreo
- ✅ Configurar controles y alertas de costo
- ✅ Aprender patrones profesionales de despliegue

## Comparación de arquitectura: Vercel vs AWS

**Vercel**:
- Next.js corre en los servidores de Vercel
- Las rutas API se ejecutan como Functions
- Deploys automáticos desde Git
- Configuración cero

**AWS**:
- Todo corre en un contenedor Docker
- FastAPI sirve API y archivos estáticos
- Deploy manual (o vía CI/CD)
- Control total de la infraestructura

Ambos enfoques son válidos: Vercel optimiza la experiencia del desarrollador, AWS ofrece control y flexibilidad.

## Próximos pasos

### Mejoras inmediatas
1. **Dominio personalizado**: configúralo en App Runner
2. **Auto-deploy**: crea un flujo con GitHub Actions
3. **Monitoreo**: agrega alarmas de CloudWatch

### Mejoras avanzadas
1. **Base de datos**: integra Amazon RDS
2. **Almacenamiento de archivos**: usa S3
3. **Caching**: agrega ElastiCache
4. **CDN**: distribuye con CloudFront
5. **Secretos**: mueve credenciales a Secrets Manager

## Referencia de resolución de problemas

### Problemas con Docker

**"Cannot connect to Docker daemon"**:
- Asegúrate de que Docker Desktop esté ejecutándose (icono de ballena)

**"Exec format error"**:
- Olvidaste `--platform linux/amd64`. Recompila con ese flag

### Problemas con AWS

**"Unauthorized" al hacer push a ECR**:
```bash
aws ecr get-login-password --region TU-REGION | docker login --username AWS --password-stdin TU-ECR-URL
```

**"Access Denied"**:
- Comprueba que tu usuario IAM tenga las políticas necesarias
- Verifica que AWS CLI use las credenciales correctas

### Problemas con la aplicación

**Clerk no autentica**:
- Verifica las tres variables de Clerk
- Asegura que la JWKS URL coincida con tu app
- Confirma que el frontend se compiló con la publishable key

**Las llamadas a la API fallan**:
- Revisa la consola del navegador por errores CORS
- Verifica que la ruta sea `/api/consultation`
- Consulta los logs de CloudWatch para errores de Python

## Conclusión

¡Felicidades por desplegar tu SaaS sanitario en AWS! Aprendiste:

1. **Conceptos base de Docker** para contenerizar aplicaciones
2. **Fundamentos de AWS** (IAM, ECR, App Runner)
3. **Despliegues de producción** con seguridad, monitoreo y control de costos
4. **Prácticas DevOps** como health checks, logging y preparación para CI/CD

Así es como los equipos profesionales despliegan aplicaciones reales. ¡Ahora tienes las habilidades para desplegar cualquier aplicación contenerizada en AWS!

## Recursos

- [Documentación de AWS App Runner](https://docs.aws.amazon.com/apprunner/)
- [Documentación de Docker](https://docs.docker.com/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)

Recuerda monitorear tus costos de AWS y pausar o eliminar recursos cuando no los uses. ¡Felices despliegues! 🚀
