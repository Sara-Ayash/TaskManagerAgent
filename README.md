# 🧠 TaskMaster: A Dialogue-Based Task Management Agent

TaskMaster is a conversational task manager built with LangGraph and LangChain. It provides a CLI-based interaction loop for managing tasks through a simple dialogue interface. Users can add tasks, update their statuses, and filter them by status—all via a guided text interface.

---

## 🚀 Features

- ✅ Add tasks with description and priority (`low`, `medium`, `high`)
- 🔄 Update task status (`pending`, `in_progress`, `done`)
- 📋 View task list filtered by status
- 🧠 Built with [LangGraph](https://github.com/langchain-ai/langgraph) for agent-like behavior
- 🔄 Simple state machine with conditional loops

---

## 🛠️ Project Structure

- `TaskManagerState`: Manages the list of tasks and current intent.
- `Task`: Data model representing a task.
- `agent()`: Main dialogue function that interacts with the user.
- `add_task()`, `update_task_status()`, `get_tasks_by_status()`: Core logic functions for task manipulation.
- `StateGraph`: Defines the stateful logic loop using LangGraph.

---

## 📦 Requirements

Make sure you have the following installed:

```bash
python>=3.9
langchain
langgraph
python-dotenv
```

 

---

## 🧪 Usage

1. Clone the repository:

```bash
git clone https://github.com/Sara-Ayash/TaskManagerAgent
cd taskmaster-agent
```

2. Run the dependencies and application:

```bash
pip install -r requirements.txt
python task_manager.py
```

3. Interact with the CLI:

```
🗣 What would you like to do?
 1️⃣  Add a new task (enter '1')
 2️⃣  Update task status (enter '2')
 3️⃣  View task list by status (enter '3')
 4️⃣  End (Say something like goodbye :) )
 ➡️  Your choice:
```

---

## 📌 Example Input

**Add Task:**
```
write blog post, high
```

**Update Task Status:**
```
88fe3bc2-d9f4-4b6c-b2f0-61f1f9c920a2, done
```

**Filter Tasks:**
```
in_progress
```

---

## 📁 Models

The following custom models are expected:

- `TaskManagerState`: Holds the list of tasks and current intent
- `Task`: Represents a single task (with `task_id`, `description`, `priority`, `status`)

Make sure these are defined in your `models.py`.

---
 