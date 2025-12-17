# Día 3: Transición a AWS Bedrock

## De OpenAI a los Servicios de IA de AWS

¡Bienvenido al Día 3! Hoy vamos a realizar un cambio arquitectónico importante: reemplazaremos OpenAI por AWS Bedrock para las respuestas de IA. Este cambio aporta varias ventajas: menor latencia (las peticiones permanecen en AWS), posibles ahorros de coste y una integración más profunda con los servicios de AWS. Aprenderás cómo las aplicaciones empresariales aprovechan los servicios de IA nativos en la nube para despliegues en producción.

## AVISO IMPORTANTE: Algo que debes tener muy en cuenta -

En Bedrock, los modelos no siempre están disponibles en todas las regiones.  
Cuando elijas el modelo a usar más abajo, puede que necesites cambiar la región (parte superior derecha de la consola) a `us-west-2` o `us-east-1` para encontrar el modelo que deseas. Esa región de AWS deberá coincidir en el código.  
Recuerda volver a tu región habitual al trabajar con otros servicios de AWS. El modelo de Bedrock no necesita ejecutarse en la misma región que el resto de tu infraestructura.

¡Gracias a Andy C (nuevamente) por resaltar este punto importante!

## Otro aviso importante:

## Bedrock, nombres de modelos, regiones y perfiles de inferencia - lee por favor

Durante este proyecto, usaremos identificadores de modelos de Bedrock como este:  
`amazon.nova-lite-v1:0`

Dependiendo de la región donde estés ejecutando y la región de Bedrock, esto podría causarte un error. Puede que necesites usar algo llamado "perfil de inferencia", especialmente si tu región por defecto es diferente a la de Bedrock. Es un cambio sencillo: solo tienes que anteponer un prefijo así a tu identificador de modelo:

`us.amazon.nova-lite-v1:0`  
o  
`eu.amazon.nova-lite-v1:0`  
(quienes estén en AP pueden usar cualquiera de los dos)

Así que si tienes un error de Bedrock, ¡prueba a añadir el prefijo "us." o "eu."! Gracias a Susan M. por señalar esto.

¡Y hay una tecnicidad adicional! Un poco tedioso, pero si utilizas estos "perfiles de inferencia", debes asegurarte de tener permiso para acceder al modelo en todas las regiones relacionadas de Bedrock, desde las pantallas de Bedrock que cubrimos hoy.

Así, si eliges `us.amazon.nova-lite-v1:0`, necesitas permiso para acceder a los modelos Nova en: us-east-1, us-east-2, us-west-2

Y si eliges `eu.amazon.nova-lite-v1:0`, necesitas permiso para acceder a los modelos Nova en: eu-central-1, eu-north-1, eu-west-1, eu-west-3

¡Uff! Si no solicitas acceso en las regiones correspondientes de Bedrock, puedes encontrarte con un error de permisos y deberás ir a la consola de Bedrock para corregirlo. ¡Puede resultar pesado!

## Qué aprenderás hoy

- **Fundamentos de AWS Bedrock** - El servicio de IA gestionado de Amazon
- **Modelos Nova** - Los modelos fundacionales más recientes de AWS
- **Permisos IAM para servicios de IA** - Buenas prácticas de seguridad
- **Selección de modelo** según coste y rendimiento
- **Monitorización con CloudWatch** para aplicaciones de IA
- **Patrones de despliegue de IA en producción** en AWS

## Entendiendo AWS Bedrock

### ¿Qué es Amazon Bedrock?

Amazon Bedrock es el servicio completamente gestionado de AWS que proporciona acceso a modelos fundacionales (FMs) de las principales empresas de IA a través de una única API. Sus principales ventajas incluyen:

- **Sin gestión de infraestructura** - Modelos de IA serverless
- **Pago por uso** - Sin costes iniciales ni cargos por inactividad
- **Baja latencia** - Los modelos se ejecutan en tu región de AWS
- **Seguridad empresarial** - Integración con IAM, endpoints VPC, cifrado
- **Variedad de modelos** - Amazon, Anthropic, Meta y más

### Modelos Amazon Nova

La familia Nova de AWS son los modelos fundacionales más recientes, optimizados para distintos casos de uso:

- **Nova Micro** - El más rápido y rentable para tareas simples
- **Nova Lite** - Rendimiento balanceado para uso general
- **Nova Pro** - Máxima capacidad para razonamiento complejo

Hoy implementaremos los tres para que puedas elegir según tu necesidad.

## Parte 1: Configura los permisos de IAM

### Paso 1: Inicia sesión como usuario root

Como necesitamos modificar permisos de IAM, ingresa como usuario root:

1. Ve a [aws.amazon.com](https://aws.amazon.com)
2. Inicia sesión con tus credenciales de **usuario root**

### Paso 2: Añade permisos de Bedrock y CloudWatch al grupo de usuarios

1. En la consola de AWS, busca **IAM**
2. Haz clic en **Grupos de usuarios** en la barra lateral izquierda
3. Haz clic en **TwinAccess** (el grupo creado el Día 2)
4. Ve a la pestaña **Permisos** → **Añadir permisos** → **Adjuntar políticas**
5. Busca y selecciona estas dos políticas:
   - **AmazonBedrockFullAccess** - Para los servicios de IA de Bedrock
   - **CloudWatchFullAccess** - Para crear paneles y ver métricas
6. Haz clic en **Adjuntar políticas**

Tu grupo TwinAccess ahora tiene estas políticas:
- AWSLambda_FullAccess
- AmazonS3FullAccess  
- AmazonAPIGatewayAdministrator
- CloudFrontFullAccess
- IAMReadOnlyAccess
- **AmazonBedrockFullAccess** (¡nuevo!)
- **CloudWatchFullAccess** (¡nuevo!)
- **AmazonDynamoDBFullAccess** (¡MUY nuevo!)

Esta última fue un aporte del estudiante Andy C (¡otra vez gracias Andy!) - sin ella podrías tener un error de permisos el Día 5.

### Paso 3: Vuelve a iniciar sesión como usuario IAM

1. Cierra la sesión de la cuenta root
2. Vuelve a ingresar como `aiengineer` con tus credenciales IAM

## Parte 2: Solicita acceso a los modelos Nova

### Paso 1: Ve a Bedrock

1. En la consola de AWS, busca **Bedrock**
2. Haz clic en el servicio **Amazon Bedrock**
3. Asegúrate de estar en la misma región que tu Lambda (ver parte superior derecha)

### Paso 2: Solicita acceso a los modelos [Ya no hace falta!]

1. En la barra lateral izquierda, haz clic en **Acceso a modelo** (bajo Modelos fundacionales)
2. Haz clic en **Gestionar acceso a modelos** o **Habilitar modelos específicos**
3. Busca la sección **Amazon**
4. Marca las casillas para estos modelos. _Ten en cuenta que puede que tengas que cambiar la región (arriba a la derecha) si no aparecen._  
   - ✅ Nova Micro
   - ✅ Nova Lite  
   - ✅ Nova Pro
5. Baja hasta el final y haz clic en **Solicitar acceso a modelo**
6. Haz clic en **Enviar**

### Paso 3: Verifica el acceso [Ya no hace falta!]

El acceso suele concederse al instante para los modelos Nova:

1. Actualiza la página
2. Debes ver el estado **Access granted** para los tres modelos Nova
3. Si no, espera 1-2 minutos y vuelve a intentarlo

## Parte 3: Entendiendo el coste de los modelos

### Precios de los modelos Nova

Los modelos Nova tienen distintas tarifas según su capacidad:

- **Nova Micro** - El más económico para tareas simples
- **Nova Lite** - Coste balanceado para uso general
- **Nova Pro** - Coste más alto para razonamiento complejo

Para ver los precios actualizados, visita: [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

En la página de precios verás:
- Coste por 1.000 tokens de entrada
- Coste por 1.000 tokens de salida
- Comparativa con otros modelos disponibles
- Diferencia de precios por región

Por lo general, Nova Micro y Lite son opciones muy rentables para la mayoría de los casos de IA conversacional.

## Parte 4: Actualiza tu código para Bedrock

### Paso 1: Actualiza los requisitos

Actualiza `twin/backend/requirements.txt` - elimina el paquete openai ya que no lo usaremos:

```
fastapi
uvicorn
python-dotenv
python-multipart
boto3
pypdf
mangum
```

Nota: Hemos eliminado `openai` de los requisitos.

### Paso 2: Actualiza el código del servidor

Reemplaza tu `twin/backend/server.py` por esta versión adaptada para Bedrock:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from context import prompt

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Configuración de CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Inicializar cliente de Bedrock
bedrock_client = boto3.client(
    service_name="bedrock-runtime", 
    region_name=os.getenv("DEFAULT_AWS_REGION", "us-east-1")
)

# Selección de modelo Bedrock
# Modelos disponibles:
# - amazon.nova-micro-v1:0  (más rápido, más barato)
# - amazon.nova-lite-v1:0   (balanceado - por defecto)
# - amazon.nova-pro-v1:0    (el más capaz, más caro)
# Recuerda el aviso: puede que necesites añadir el prefijo us. o eu. al id de modelo
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

# Configuración de almacenamiento de memoria
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "")
MEMORY_DIR = os.getenv("MEMORY_DIR", "../memory")

# Inicializar cliente S3 si es necesario
if USE_S3:
    s3_client = boto3.client("s3")


# Modelos de petición/respuesta
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


# Funciones de gestión de memoria
def get_memory_path(session_id: str) -> str:
    return f"{session_id}.json"


def load_conversation(session_id: str) -> List[Dict]:
    """Cargar historial de conversación desde el almacenamiento"""
    if USE_S3:
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return []
            raise
    else:
        # Almacenamiento en archivo local
        file_path = os.path.join(MEMORY_DIR, get_memory_path(session_id))
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []


def save_conversation(session_id: str, messages: List[Dict]):
    """Guardar historial de conversación en el almacenamiento"""
    if USE_S3:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=get_memory_path(session_id),
            Body=json.dumps(messages, indent=2),
            ContentType="application/json",
        )
    else:
        # Almacenamiento en archivo local
        os.makedirs(MEMORY_DIR, exist_ok=True)
        file_path = os.path.join(MEMORY_DIR, get_memory_path(session_id))
        with open(file_path, "w") as f:
            json.dump(messages, f, indent=2)


def call_bedrock(conversation: List[Dict], user_message: str) -> str:
    """Llama a AWS Bedrock con el historial de conversación"""
    
    # Construir mensajes en formato Bedrock
    messages = []
    
    # Añadir prompt de sistema como primer mensaje de usuario (convención Bedrock)
    messages.append({
        "role": "user", 
        "content": [{"text": f"System: {prompt()}"}]
    })
    
    # Añadir historial de conversación (limitar a últimos 10 intercambios para controlar el contexto)
    for msg in conversation[-20:]:  # Últimos 10 intercambios ida y vuelta
        messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })
    
    # Añadir mensaje actual del usuario
    messages.append({
        "role": "user",
        "content": [{"text": user_message}]
    })
    
    try:
        # Llamar a Bedrock usando la API converse
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        )
        
        # Extraer el texto de la respuesta
        return response["output"]["message"]["content"][0]["text"]
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ValidationException':
            # Gestionar errores de formato de mensaje
            print(f"Error de validación de Bedrock: {e}")
            raise HTTPException(status_code=400, detail="Formato de mensaje no válido para Bedrock")
        elif error_code == 'AccessDeniedException':
            print(f"Acceso denegado a Bedrock: {e}")
            raise HTTPException(status_code=403, detail="Acceso denegado al modelo Bedrock")
        else:
            print(f"Error de Bedrock: {e}")
            raise HTTPException(status_code=500, detail=f"Error de Bedrock: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "API Gemelo Digital IA (Con AWS Bedrock)",
        "memory_enabled": True,
        "storage": "S3" if USE_S3 else "local",
        "ai_model": BEDROCK_MODEL_ID
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "use_s3": USE_S3,
        "bedrock_model": BEDROCK_MODEL_ID
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generar session_id si no se proporciona
        session_id = request.session_id or str(uuid.uuid4())

        # Cargar historial de conversación
        conversation = load_conversation(session_id)

        # Llamar a Bedrock para obtener la respuesta
        assistant_response = call_bedrock(conversation, request.message)

        # Actualizar historial de conversación
        conversation.append(
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()}
        )
        conversation.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Guardar la conversación
        save_conversation(session_id, conversation)

        return ChatResponse(response=assistant_response, session_id=session_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en endpoint chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Recuperar historial de conversación"""
    try:
        conversation = load_conversation(session_id)
        return {"session_id": session_id, "messages": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Cambios clave explicados

1. **Se eliminó la importación de OpenAI** - Ya no se usa `from openai import OpenAI`
2. **Se añadió el cliente de Bedrock** - Utilizando boto3 para conectar con Bedrock
3. **Nueva función `call_bedrock`** - Gestiona el formato de mensajes de Bedrock
4. **Selección de modelo por variable de entorno** - Fácil alternar entre modelos Nova
5. **Mejor gestión de errores** - Maneja específicamente los errores propios de Bedrock

## Parte 5: Despliega en Lambda

### Paso 1: Actualiza las variables de entorno de Lambda

1. En la consola de AWS, ve a **Lambda**
2. Haz clic en tu función `twin-api`
3. Ve a **Configuración** → **Variables de entorno**
4. Haz clic en **Editar**
5. Añade estas nuevas variables:
   - Clave: `DEFAULT_AWS_REGION` | Valor: `us-east-1` (o tu región)
   - Clave: `BEDROCK_MODEL_ID` | Valor: `amazon.nova-lite-v1:0` recuerda que puede requerir el prefijo "us." o "eu." si obtienes un error de Bedrock  
6. Ahora puedes eliminar `OPENAI_API_KEY` ya que no lo usas
7. Haz clic en **Guardar**

### Opciones de ID de modelo

Puedes cambiar el `BEDROCK_MODEL_ID` por cualquiera de estos, y puede que necesites añadir el prefijo "us." o "eu.", como explicamos arriba:  
- `amazon.nova-micro-v1:0` - El más rápido y barato
- `amazon.nova-lite-v1:0` - Balanceado (recomendado)
- `amazon.nova-pro-v1:0` - El más capaz pero más caro

### Paso 2: Añade permisos Bedrock a Lambda

Tu función Lambda necesita permisos para llamar a Bedrock:

1. En Lambda → **Configuración** → **Permisos**
2. Haz clic en el nombre de la ejecución de rol (se abre IAM)
3. Haz clic en **Añadir permisos** → **Adjuntar políticas**
4. Busca y selecciona: **AmazonBedrockFullAccess**
5. Haz clic en **Añadir permisos**

### Paso 3: Reconstruye y despliega el paquete de Lambda

Como cambiamos requirements.txt, instala dependencias y reconstruye el paquete:

```bash
cd backend
uv add -r requirements.txt
uv run deploy.py
```

Esto creará un nuevo `lambda-deployment.zip` con las dependencias actualizadas.

### Paso 4: Sube a Lambda

Subiremos el código a través de S3, lo cual es más fiable para paquetes grandes o conexiones lentas.

**Mac/Linux:**

```bash
# Carga las variables de entorno
source .env

# Navega al backend
cd backend

# Crea un nombre único de bucket S3 para el despliegue
DEPLOY_BUCKET="twin-deploy-$(date +%s)"

# Crea el bucket
aws s3 mb s3://$DEPLOY_BUCKET --region $DEFAULT_AWS_REGION

# Sube tu archivo zip a S3
aws s3 cp lambda-deployment.zip s3://$DEPLOY_BUCKET/ --region $DEFAULT_AWS_REGION

# Actualiza la función Lambda desde S3
aws lambda update-function-code \
    --function-name twin-api \
    --s3-bucket $DEPLOY_BUCKET \
    --s3-key lambda-deployment.zip \
    --region $DEFAULT_AWS_REGION

# Limpieza: elimina el bucket temporal
aws s3 rm s3://$DEPLOY_BUCKET/lambda-deployment.zip
aws s3 rb s3://$DEPLOY_BUCKET
```

**Windows (PowerShell): comenzando en la raíz del proyecto**

```powershell
# Carga las variables de entorno
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}

# Navega al backend
cd backend

# Crea un nombre único de bucket S3 para el despliegue
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$deployBucket = "twin-deploy-$timestamp"

# Crea el bucket
aws s3 mb s3://$deployBucket --region $env:DEFAULT_AWS_REGION

# Sube tu archivo zip a S3
aws s3 cp lambda-deployment.zip s3://$deployBucket/ --region $env:DEFAULT_AWS_REGION

# Actualiza la función Lambda desde S3
aws lambda update-function-code `
    --function-name twin-api `
    --s3-bucket $deployBucket `
    --s3-key lambda-deployment.zip `
    --region $env:DEFAULT_AWS_REGION

# Limpieza: elimina el bucket temporal
aws s3 rm s3://$deployBucket/lambda-deployment.zip
aws s3 rb s3://$deployBucket
```

**Alternativa: Subida directa (solo para conexiones rápidas)**

Si tienes una conexión rápida y estable, puedes subir directamente:

```bash
aws lambda update-function-code \
    --function-name twin-api \
    --zip-file fileb://lambda-deployment.zip \
    --region $DEFAULT_AWS_REGION
```

**Nota**: Se recomienda el método S3 porque:
- La subida a S3 puede reanudarse si se interrumpe
- Lambda obtiene el archivo directamente de S3 (más rápido que subir con CLI)
- Funciona mejor con firewalls corporativos y VPNs
- Más fiable si el paquete supera los 10MB

Espera a que finalice la actualización. Deberías ver en la salida `"LastUpdateStatus": "Successful"`.

### Paso 5: Prueba la función Lambda

1. En la consola de Lambda, ve a la pestaña **Probar**
2. Usa tu evento de prueba `HealthCheck` existente
3. Haz clic en **Probar**
4. Comprueba la respuesta - ahora debe mostrar el modelo Bedrock:

```json
{
  "statusCode": 200,
  "body": "{\"status\":\"healthy\",\"use_s3\":true,\"bedrock_model\":\"amazon.nova-lite-v1:0\"}"
}
```

## Parte 6: Prueba tu Gemelo con Bedrock

### Paso 1: Prueba vía API Gateway

Prueba tu API directamente con curl:

```bash
curl https://TU-API-ID.execute-api.us-east-1.amazonaws.com/health
```

Deberías ver el modelo Bedrock en la respuesta.

### Paso 2: Prueba vía CloudFront

1. Accede a tu URL de CloudFront: `https://TU-DISTRIBUIDOR.cloudfront.net`
2. Inicia una conversación con tu gemelo
3. Comprueba que el chat funcione bien
4. Verifica que las respuestas lleguen correctamente

## Parte 7: Monitorización con CloudWatch

Vamos a configurar la monitorización para tu uso de Bedrock y el rendimiento de Lambda.

### Paso 1: Ver métricas de Lambda

1. En la consola de AWS, ve a **CloudWatch**
2. Haz clic en **Métricas** → **Todas las métricas**
3. Haz clic en **Lambda** → **Por nombre de función**
4. Selecciona `twin-api`
5. Revisa estas métricas clave:
   - ✅ Invocaciones
   - ✅ Duración
   - ✅ Errores
   - ✅ Throttlings

### Paso 2: Ver métricas de Bedrock

1. En las métricas de CloudWatch, haz clic en **AWS/Bedrock**
2. Haz clic en **Por id de modelo**
3. Selecciona tu modelo Nova
4. Revisa estas métricas:
   - **InvocationLatency** - Tiempo de respuesta
   - **Invocations** - Número de peticiones
   - **InputTokenCount** - Tokens enviados al modelo
   - **OutputTokenCount** - Tokens generados por el modelo

### Paso 3: Ver logs de Lambda

1. En CloudWatch, haz clic en **Grupos de logs**
2. Haz clic en `/aws/lambda/twin-api`
3. Haz clic en el stream de logs más reciente
4. Puedes ver:
   - Cada invocación de la función
   - Llamadas a la API de Bedrock
   - Errores o advertencias
   - Tiempos de respuesta

### Paso 4: Crea un panel CloudWatch (opcional)

Vamos a crear un panel para monitorizar todo de un vistazo:

1. En CloudWatch, haz clic en **Paneles** → **Crear panel**
2. Nombre: `twin-monitoring`
3. Añade widgets:

**Widget 1: Invocaciones de Lambda**
- Tipo: Línea
- Métrica: Lambda → twin-api → Invocations
- Estadística: Suma
- Periodo: 5 minutos

**Widget 2: Duración de Lambda**
- Tipo: Línea  
- Métrica: Lambda → twin-api → Duration
- Estadística: Promedio
- Periodo: 5 minutos

**Widget 3: Errores de Lambda**
- Tipo: Número
- Métrica: Lambda → twin-api → Errors
- Estadística: Suma
- Periodo: 1 hora

**Widget 4: Invocaciones de Bedrock**
- Tipo: Línea
- Métrica: AWS/Bedrock → Tu Modelo → Invocations
- Estadística: Suma
- Periodo: 5 minutos

### Paso 5: Configura la monitorización de costes

Monitorea tus costes de AWS:

1. Ve a **AWS Cost Explorer** (búscalo en la consola)
2. Haz clic en **Cost Explorer** → **Launch Cost Explorer**
3. Filtra por:
   - Servicio: Bedrock
   - Tiempo: Últimos 7 días
4. Puedes ver cómo van aumentando tus costes de Bedrock

### Paso 6: Crea una alerta de presupuesto (Recomendado)

1. En la consola de AWS, busca **Billing**
2. Haz clic en **Budgets** → **Create budget**
3. Elige **Cost budget**
4. Configura:
   - Nombre: `twin-budget`
   - Presupuesto mensual: $10 (o lo que decidas)
   - Alerta al 80% del presupuesto
5. Introduce tu email para notificaciones
6. Haz clic en **Create budget**

## Parte 8: Comparativa de rendimiento (opcional)

### Prueba los diferentes modelos

Compara los modelos Nova. Cambia la variable de entorno `BEDROCK_MODEL_ID` en Lambda para probar cada uno:

1. **Nova Micro** (`amazon.nova-micro-v1:0`)
   - Respuesta más rápida (típicamente <1 segundo)
   - Bueno para preguntas/respuestas simples
   - Coste más bajo

2. **Nova Lite** (`amazon.nova-lite-v1:0`)
   - Rendimiento equilibrado (1-2 segundos)
   - Bueno para la mayoría de conversaciones
   - Recomendado para producción

3. **Nova Pro** (`amazon.nova-pro-v1:0`)
   - Respuestas más sofisticadas (2-4 segundos)
   - Ideal para razonamiento complejo
   - Coste más alto

### Monitoriza los tiempos de respuesta

Después de probar cada modelo, revisa en CloudWatch:

1. Ve a CloudWatch → Grupos de logs → `/aws/lambda/twin-api`
2. Usa Log Insights con esta consulta:

```
fields @timestamp, @duration
| filter @type = "REPORT"
| stats avg(@duration) as avg_duration,
        min(@duration) as min_duration,
        max(@duration) as max_duration
by bin(5m)
```

Esto muestra los tiempos de ejecución de tu Lambda por modelo.

## Resolución de problemas

### Errores de "Access Denied"

Si ves errores de denegación de acceso:

1. Verifica los permisos de IAM:
   - El rol de ejecución de Lambda tiene `AmazonBedrockFullAccess`
   - Tu usuario IAM tiene permisos para Bedrock
2. Verifica acceso al modelo:
   - Ve a Bedrock → Acceso a modelo
   - Asegúrate de que los modelos Nova tienen "Acceso concedido"
3. Verifica la región:
   - Bedrock debe estar en la misma región que Lambda

### Errores de "Model Not Found"

1. Revisa que el identificador sea correcto:
   - `amazon.nova-micro-v1:0` (no v1.0 ni v1)
   - Sensible a mayúsculas y minúsculas
2. Verifica que el modelo esté disponible en tu región
3. Confirma que tienes acceso concedido

### Latencia alta

Si las respuestas son lentas:

1. Prueba Nova Micro para respuestas más rápidas
2. Revisa el timeout de Lambda (debería ser 30+ segundos)
3. Consulta los logs de CloudWatch para cuellos de botella
4. Considera aumentar la memoria de Lambda (más CPU rápido)

### El chat no funciona

1. Mira los logs de CloudWatch para errores específicos
2. Prueba la función Lambda directamente desde la consola
3. Verifica que todas las variables de entorno estén configuradas
4. Comprueba que API Gateway reenvíe bien las peticiones

## Consejos de optimización de costes

### Cómo elegir el modelo correcto

- **Nova Micro**: Úsalo para saludos, FAQs simples, consultas básicas
- **Nova Lite**: Úsalo para conversaciones normales, preguntas generales
- **Nova Pro**: Para análisis complejo, respuestas detalladas

### Reduciendo los costes

1. **Limita la ventana de contexto** - Se envían los últimos 20 mensajes; reduce si lo necesitas
2. **Cachea respuestas comunes** - Guarda FAQs en DynamoDB
3. **Configura max tokens apropiadamente** - Aquí usamos 2000; ajusta según lo que requieras
4. **Monitorea el uso** - Usa alertas de presupuesto
5. **Aplica throttling** - Implementa límite de peticiones en API Gateway

### Costes mensuales estimados

Tus costes dependen de:
- Número de conversaciones al mes
- Longitud media de las conversaciones
- Modelo Nova elegido
- Uso de Lambda, API Gateway y S3

Consulta la página de [Precios de AWS Bedrock](https://aws.amazon.com/bedrock/pricing/) y usa la calculadora de precios para estimar tu caso.

## ¡Lo que has logrado hoy!

- ✅ Transición de OpenAI a AWS Bedrock
- ✅ Configuración de permisos IAM para servicios de IA
- ✅ Implementación de tres modelos de IA diferentes
- ✅ Despliegue de la integración con Bedrock en Lambda
- ✅ Configuración de monitorización con CloudWatch
- ✅ Creación de alertas y seguimiento de costes
- ✅ Aprendizaje de patrones de despliegue de IA empresarial

## Repaso de la arquitectura

Tu arquitectura actualizada:

```
Navegador del usuario
    ↓ HTTPS
CloudFront (CDN)
    ↓ 
S3 Sitio Estático (Frontend)
    ↓ Llamadas API HTTPS
API Gateway
    ↓
Función Lambda (Backend)
    ↓
    ├── AWS Bedrock (respuestas IA)  ← ¡NUEVO!
    └── Bucket S3 de memoria (persistencia)
```

Ahora todos los servicios permanecen en AWS, proporcionando:
- Menor latencia (sin llamadas API externas)
- Mejor seguridad (integración IAM)
- Potencial ahorro de costes
- Facturación y monitorización unificada

## Siguientes pasos

Mañana (Día 4) vamos a:
- Introducir Infraestructura como Código con Terraform
- Automatizar todo el proceso de despliegue
- Implementar gestión de entornos (desarrollo/producción/pruebas)
- Añadir características avanzadas como memoria en DynamoDB
- Configurar gestión apropiada de secretos

¡Ahora tu Gemelo Digital está impulsado 100% por servicios AWS; una auténtica aplicación cloud-native!

## Recursos

- [Documentación de AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [Precios de Bedrock](https://aws.amazon.com/bedrock/pricing/)
- [Documentación de modelos Nova](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
- [Documentación de CloudWatch](https://docs.aws.amazon.com/cloudwatch/)
- [Gestión de costes AWS](https://aws.amazon.com/cost-management/)

¡Enhorabuena por integrar AWS Bedrock con éxito! 🚀