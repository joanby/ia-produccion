from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from typing import List
from pydantic import BaseModel, Field

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

app = BedrockAgentCoreApp()


class ToDoItem(BaseModel):
    description: str = Field(..., description="El texto que describe la tarea")
    completed: bool = Field(False, description="Si la tarea ha sido completada o no")


todos = []

system_prompt = """
Se te presenta un problema para resolver, utilizando tus herramientas de lista de tareas (todo) para planificar una serie de pasos y realizarlos uno a uno.
También tienes acceso a la herramienta execute_python para ejecutar código Python.
Tu plan debe incluir la resolución del problema sin Python, y luego escribir y ejecutar código Python para validar tu solución.
Para utilizar la herramienta execute_python en la validación, debes tener una tarea en tu lista que empiece con "Escribe código Python para...".
Ahora utiliza las herramientas de la lista de tareas, crea un plan, ejecuta los pasos y responde con la solución.
"""

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


tools = [create_todos, mark_complete, list_todos, execute_python]
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