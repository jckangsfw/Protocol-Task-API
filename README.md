# Protocol Task API

A simple API built with FastAPI that reads clinical trial protocol text and turns it into a task list.
It is a small practice version of the AI protocol parser for my capstone project.

## How to run

```
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs in the browser to try every endpoint.

## Endpoints

| Method | URL | What it does |
|--------|-----|--------------|
| POST   | `/parse`           | Send protocol text, get back the tasks it found
| GET    | `/tasks`           | List all tasks (`?done=false` shows only unfinished ones)
| GET    | `/tasks/{task_id}` | Get one task (returns 404 if it doesn't exist)
| POST   | `/tasks`           | Add a task by hand
| PUT    | `/tasks/{task_id}/complete` | Mark a task as done
| DELETE | `/tasks/{task_id}` | Delete a task

## How the parser works

It splits the text into sentences and keeps any sentence with an action word such as
"collect", "measure", "record", or "administer". Tasks are stored in memory, so they reset
when the server restarts.

## Example

Request to `POST /parse`:

```json
{
  "text": "At each visit, staff will measure blood pressure. Collect a blood sample at Week 0. The study lasts 12 weeks."
}
```

Response: two tasks ("At each visit, staff will measure blood pressure" and "Collect a blood sample at Week 0").
The last sentence has no action word, so it is skipped.