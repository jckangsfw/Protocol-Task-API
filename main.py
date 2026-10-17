from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Protocol Task API",
    description="A simple API that reads clinical trial protocol text and turns it into a task list.",
)

# Words that usually mean "someone has to do something" in a protocol
ACTION_WORDS = ["collect", "measure", "record", "administer", "schedule", "review", "obtain", "perform"]

# Tasks are stored in memory (they reset when the server restarts)
tasks = []
next_id = 1


class ProtocolText(BaseModel):
    text: str


class NewTask(BaseModel):
    description: str


def add_task(description):
    global next_id
    task = {"id": next_id, "description": description, "done": False}
    tasks.append(task)
    next_id += 1
    return task


def find_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/parse", status_code=201)
def parse_protocol(protocol: ProtocolText):
    """Split the protocol into sentences and save the ones that contain an action word as tasks."""
    sentences = protocol.text.replace("\n", " ").split(". ")
    created = []
    for sentence in sentences:
        sentence = sentence.strip().rstrip(".")
        if any(word in sentence.lower() for word in ACTION_WORDS):
            created.append(add_task(sentence))
    if not created:
        raise HTTPException(status_code=422, detail="No tasks found in the protocol text")
    return {"tasks_created": len(created), "tasks": created}


@app.get("/tasks")
def get_tasks(done: bool | None = None):
    """List all tasks. Use ?done=true or ?done=false to filter."""
    if done is None:
        return tasks
    return [task for task in tasks if task["done"] == done]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return find_task(task_id)


@app.post("/tasks", status_code=201)
def create_task(new_task: NewTask):
    """Add a task by hand."""
    return add_task(new_task.description)


@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    task = find_task(task_id)
    task["done"] = True
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
