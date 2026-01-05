# ¡Bienvenido de nuevo al Repositorio de Producción! 👋

## Y bienvenido al Gran Final de **AWS Bedrock AgentCore** 🎉

![Imagen del Curso](../assets/finale.png)

*Si estás viendo esto en **Cursor**, haz clic derecho sobre el nombre del archivo en el Explorador de la izquierda y selecciona **“Open preview”** para verlo con formato completo.*

---

### 🧩 Paso 1: IAM (sí… 😅)

¡Ya eres todo un profesional, así que ahora recibirás instrucciones de nivel experto!

1. Inicia sesión en la **consola de AWS** como usuario raíz.
2. Ve a **IAM → Grupos de Usuarios (User Groups)**.
3. Crea un nuevo grupo de usuarios llamado **"AgentAccess"**.
4. Añádelo al usuario **aiengineer**.
5. Asigna las siguientes políticas:

   * `AmazonBedrockFullAccess`
   * `AWSCodeBuildAdminAccess`
   * `BedrockAgentCoreFullAccess`

Además, a partir de hoy, necesitas tener acceso al modelo **Claude Sonnet 4** en la región **us-west-2**.

#### Ahora inicia sesión como tu usuario IAM.

1. Navega a **AWS Bedrock AgentCore**.
2. Selecciona **Observability** en la barra lateral.
3. Activa la opción correspondiente (puedes habilitar solo la versión gratuita si lo prefieres).

Y guarda los cambios. ✅

---

### 📖 Paso 2: Lectura Recomendada

Página principal de **Amazon Bedrock AgentCore:**
🔗 [https://aws.amazon.com/bedrock/agentcore/](https://aws.amazon.com/bedrock/agentcore/)

Guía de usuario, ejemplos y documentación de referencia:
🔗 [https://aws.github.io/bedrock-agentcore-starter-toolkit/index.html](https://aws.github.io/bedrock-agentcore-starter-toolkit/index.html)

Más enlaces de interés:

* **SDK de Python de AgentCore:**
  🔗 [https://github.com/aws/bedrock-agentcore-sdk-python](https://github.com/aws/bedrock-agentcore-sdk-python)
* **AgentCore Starter Toolkit (CLI):**
  🔗 [https://github.com/aws/bedrock-agentcore-starter-toolkit](https://github.com/aws/bedrock-agentcore-starter-toolkit)

---

### ⚙️ Paso 3: Presentación del Proyecto *uv* en esta Carpeta

He añadido solo unas pocas dependencias a este proyecto:

* `bedrock-agentcore`
* `strands-agents`
* `bedrock-agentcore-starter-toolkit`
* `pydantic`

Así que si ejecutas:

```bash
cd finale
uv sync
```

tendrás todos esos paquetes instalados.

---

### 🤖 Paso 4: Crear tu Primer Agente

Crea un nuevo archivo en este directorio llamado **`first.py`** y coloca este código:


```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
import math

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    """Realiza una llamada simple a Strands Agent"""
    user_message = payload.get("prompt")
    result = agent(user_message)
    return result.message

if __name__ == "__main__":
    app.run()
```

Ahora ejecuta este comando para probar el servidor localmente:

```bash
uv run first.py
```

Deja este servidor en ejecución y abre una **nueva terminal** en Cursor. Envía un mensaje con el siguiente comando:

```bash
curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d '{"prompt": "Hola, ¿¿me escuchas??"}'
```

---

### ☁️ Paso 5 - ¡Despliega!

Aquí viene el gran comando — pero también presta atención al **valiosísimo consejo del estudiante Andy C.** 👇

```bash
uv run agentcore configure -e first.py
```

y selecciona todas las opciones por defecto.

---

📝 **NOTA DE ANDY C.:**

> Mi región predeterminada de AWS estaba configurada como **“us-east-2”**, pero el modelo Claude que usamos solo está disponible en **“us-west-2”**.
> Esto provocó varios errores al intentar desplegar el conjunto de AgentCore.
> Se soluciona fácilmente añadiendo un *flag* que apunte a la región del modelo:
>
> ```bash
> uv run agentcore configure -e first.py --region us-west-2
> ```
>
> Una vez hecho esto, ¡todo en la lección de AgentCore funcionó sin problemas!
> Fue tan divertido como sencillo. 😄

---

Después de ejecutar el comando anterior (ya sea el mío o el de Andy si tu Bedrock está en otra región):

```bash
uv run agentcore launch
```

Y luego…

```bash
uv run agentcore invoke '{"prompt": "Hola, ¿¿me escuchas??"}'
```

---

¡Increíble! 😲 ¿Te das cuenta de todo lo que acaba de ocurrir?

* **AgentCore construyó un contenedor.**
* **AgentCore lo desplegó en ECR.**
* **AgentCore configuró automáticamente IAM.**
* **AgentCore desplegó algo similar a App Runner.**
* **AgentCore le envió un mensaje.**

💥 ¡Es como una semana entera de trabajo, en un solo minuto!

---

### 🧠 Paso 6 - AHORA: Herramientas con *Strands*

Agrega esto al inicio de tu archivo **`first.py`**, justo debajo de los *imports* pero antes de las asignaciones de variables:


```python
@tool
def take_square_root(input_number: float):
    """Calcula la raíz cuadrada de un número dado"""
    return str(math.sqrt(input_number))
```

Y cambia `agent = Agent()` por `agent = Agent(tools=[take_square_root])`

Y luego:

`uv run agentcore launch`

`uv run agentcore invoke '{"prompt": "Usa tu herramienta para calcular la raíz cuadrada de 1234567 con 3 decimales"}'`

¡Eso es uso de herramientas! 🔧✨

---

### 🌀 Paso 7

Y ahora… ¡un nuevo y más potente agente — *el looper*! 🔁

Primero, elimina el archivo **`first.py`**, ya que solo podemos tener **un módulo de Python con un punto de entrada (entrypoint)**.

Crea un nuevo archivo llamado **`looper.py`** con el siguiente contenido:


```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from typing import List
from pydantic import BaseModel, Field


app = BedrockAgentCoreApp()


class ToDoItem(BaseModel):
    description: str = Field(..., description="El texto que describe la tarea")
    completed: bool = Field(False, description="Si la tarea ha sido completada o no")


todos = []

system_prompt = """
Se te da un problema para resolver, utilizando tus herramientas de lista de tareas para planificar una lista de pasos, luego llevando a cabo cada paso en orden.
Ahora utiliza las herramientas de la lista de tareas, crea un plan, realiza los pasos y responde con la solución.
"""

def get_todo_report() -> str:
    """Obtiee un reporte de todas las tareas."""
    result = ""
    for index, todo in enumerate(todos):
        completed = "X" if todo.completed else " "
        start = "[strike][green]" if todo.completed else ""
        end = "[/strike][/green]" if todo.completed else ""
        result += f"Todo #{index + 1}: [{completed}] {start}{todo.description}{end}\n"
    return result


@tool
def create_todos(descriptions: List[str]) -> str:
    """Agregar nuevas tareas a partir de una lista de descripciones y devolver la lista completa"""
    for desc in descriptions:
        todos.append(ToDoItem(description=desc))
    return get_todo_report()


@tool
def mark_complete(index: int) -> str:
    """Marca como completada la tarea en la posición dada (empezando desde 1) y devuelve la lista completa"""
    if 1 <= index <= len(todos):
        todos[index - 1].completed = True
    else:
        return "No todo at this index."
    return get_todo_report()


@tool
def list_todos() -> str:
    """Devuelve la lista completa de tareas, marcando las completadas."""
    return get_todo_report()


tools = [create_todos, mark_complete, list_todos]
agent = Agent(system_prompt=system_prompt, tools=tools)


@app.entrypoint
async def invoke(payload):
    """Our Agent function"""
    user_message = payload.get("prompt")
    stream = agent.stream_async(user_message)
    async for event in stream:
        if "data" in event:
            yield event["data"]  # Stream data chunks
        elif "message" in event:
            yield "\n" + get_todo_report()


if __name__ == "__main__":
    app.run()

```

`uv run agentcore configure -e looper.py`

Selecciona todos los valores por defecto y luego:

`uv run agentcore launch`

Y finalmente...

`uv run agentcore invoke '{"prompt": "Un tren sale de Boston a las 2:00 pm viajando a 60 mph. Otro tren sale de Nueva York a las 3:00 pm viajando a 80 mph hacia Boston. ¿Cuándo se encuentran?"}'`

¡Qué genial es eso! 🤩🚆

---

### 🧩 Paso 8: Añadir el **Code Interpreter**

Debajo de los *imports*, añade este bloque de código:


```python
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
import json

code_client = CodeInterpreter("us-west-2")

@tool
def execute_python(code: str) -> str:
    """Ejecuta código Python en el intérprete de código."""
    response = code_client.invoke("executeCode", {"language": "python", "code": code})
    output = []
    for event in response["stream"]:
        if "result" in event and "content" in event["result"]:
            content = event["result"]["content"]
            output.append(content)
    return json.dumps(output[-1])
```

Actualiza el prompt de sistema:

```python
system_prompt = """
Se te presenta un problema para resolver, utilizando tus herramientas de lista de tareas (todo) para planificar una serie de pasos y realizarlos uno a uno.
También tienes acceso a la herramienta execute_python para ejecutar código Python.
Tu plan debe incluir la resolución del problema sin Python, y luego escribir y ejecutar código Python para validar tu solución.
Para utilizar la herramienta execute_python en la validación, debes tener una tarea en tu lista que empiece con "Escribe código Python para...".
Ahora utiliza las herramientas de la lista de tareas, crea un plan, ejecuta los pasos y responde con la solución.
"""
```

Actualiza el método **`get_todo_report()`** para resaltar las tareas relacionadas con código de programación:

```python
def get_todo_report() -> str:
    """Obtén un informe de todas las tareas pendientes."""
    result = ""
    for index, todo in enumerate(todos):
        completed = "X" if todo.completed else " "
        start = "[strike][green]" if todo.completed else ""
        end = "[/strike][/green]" if todo.completed else ""
        start += "[red]" if "python" in todo.description.lower() else ""
        end += "[/red]" if "python" in todo.description.lower() else ""
        result += f"Todo #{index + 1}: [{completed}] {start}{todo.description}{end}\n"
    return result
```

Y el paso final — cambia la línea que define las herramientas para añadir la nueva función:

```python
tools = [create_todos, mark_complete, list_todos, execute_python]
```

Ahora ejecuta:

```bash
uv run agentcore launch
```

Y luego…

```bash
uv run agentcore invoke '{"prompt": "Un tren sale de Boston a las 14:00 viajando a 60 mph. Otro tren sale de Nueva York a las 15:00 viajando a 80 mph hacia Boston. ¿Cuándo se encuentran?"}'
```

¡Qué divertido! 😄🚄

---

### 🔍 Paso 9: Observabilidad

1. Vuelve a la **consola de AWS** con tu usuario IAM.
2. Entra en el servicio **Amazon Bedrock AgentCore**.
3. Selecciona **Observability** en el menú lateral.
4. Examina tus **agentes, sesiones y trazas**.
5. Fíjate en cómo el sistema realiza reintentos ante problemas de *throttling* — eso explica por qué algunas ejecuciones pueden parecer lentas.

---

## ✅ ¡Y LISTO!

Despliegue de agentes en cuestión de minutos. ⚡

🎯 **Tu tarea:** ¡sigue adelante!
Prueba a añadir un **frontend en Next.js**, incorpora la otra herramienta (automatización del navegador) y convierte todo esto en tu **asistente personal completo** 🤖💼
