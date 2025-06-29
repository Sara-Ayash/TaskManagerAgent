import os
import uuid
from dotenv import load_dotenv
from typing import Literal, List
from models import TaskManagerState, Task

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage  
from langchain_core.messages import ToolMessage  
from langchain_core.messages import SystemMessage  
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages

load_dotenv()

def add_task(state: TaskManagerState, new_task: str):
    """
    Add a new task to the task manager.
    """
    if not new_task:
        raise ValueError("Description required, Priority is optional (default is low)")

    parts = new_task.split(",")
    
    description = parts[0].strip()
    
    if len(parts) > 1:
        priority = parts[1].strip()
    else:
        print("❗ No priority provided, defaulting to low")
        priority = "low"    

    if not priority in ["low", "medium", "high"]:
        raise ValueError("Priority must be one of: low, medium, high")

    task: Task = state.add_task(priority, description)
    print(f"✅ New task added: {task}")

    return state

def update_task_status(state: TaskManagerState, task_to_update_status: str):
    """
    Update a task in the task manager.
    """
    parts = task_to_update_status.split(",")
    if len(parts) < 2:
        raise ValueError("Task ID and status are required)")
   
    task_id = parts[0].strip()
    status = parts[1].strip()

    task_to_update: Task = state.get_task_by_id(task_id)
    previous_status = task_to_update.status
    if not task_to_update:
        raise ValueError(f"Task not found: {task_id}")

    if status == task_to_update.status:
        raise ValueError(f"❗ Task is already in status: {status}")

    if status not in ["pending", "in_progress", "done"]:
        raise ValueError("Status must be one of: pending, in_progress, done")

    task = state.update_task_status(task_id, status)
    if task:
        print(f"✅ Task status updated from '{previous_status}' to '{status}': {task}")
    else:
        print(f"❌ Task not found: {task_id}")

    return state


def get_tasks_by_status(state: TaskManagerState, status: Literal["pending", "in_progress", "done"] = "all"):
    """
    Get tasks by status.
    """
    try:
        tasks = state.get_tasks_by_status(status)
        if tasks:
            tasks_str = "\n".join([f"[{task.task_id}] Description: {task.description}, Priority: {task.priority }, Status: {task.status}" for task in tasks])
            print( f"✅ Found {len(tasks)} tasks with status '{status}':\n" + tasks_str)
        else:
            print( f"No tasks found with status '{status}'")
    except ValueError as e:
        print(f"❌ {str(e)}")
    return state


def should_continue(state: TaskManagerState) -> str:
    """
    Determine if the agent should continue or end.
    """
    if state.intent == "end":
        return "end"
    return "continue"


def validate_task_input(new_task: str):
    """
    Validate the task input.
    """
    if not new_task:
        raise ValueError("Description required, Priority is optional (default is low)")

    parts = new_task.split(",")
    
    description = parts[0].strip()
    
    if len(parts) > 1:
        priority = parts[1].strip()
    else:
        print("❗ No priority provided, defaulting to low")
        priority = "low"

    if not priority in ["low", "medium", "high"]:
        raise ValueError("Priority must be one of: low, medium, high")


def agent(state: TaskManagerState) -> TaskManagerState:
    user_input = input(
        "\n🗣  What would you like to do?\n"
        " 1️⃣  Add a new task (enter '1')\n"
        " 2️⃣  Update task status (enter '2')\n"
        " 3️⃣  View task list by status (enter '3')\n"
        " 4️⃣  End (Say something like goodbye :) )\n"
        " ➡️  Your choice: "
    )
 
    # Add a new task
    if user_input == "1":
        new_task = input("\n🗣  please enter the task you want to add? Usage: <description>, <priority>\n� USER: ")
        try:
            add_task(state, new_task)
            state.intent = "add_task"
        except ValueError as e:
            print(f"❌ Invalid task input: {str(e)} \nUsage: <description>, <priority>\nPlease try again.")
        finally:
            return state

    # Update task status
    elif user_input == "2":
        task_to_update_status = input("\n🗣  Please enter the task you want to update its status? Usage: <task_id>, <status>\n� USER: ")
        try:
            update_task_status(state, task_to_update_status)
            state.intent = "update_task_status"
        except ValueError as e:
            print(f"❌ Invalid task input: {str(e)} \nUsage: <task_id>, <status>\nPlease try again.")
        finally:
            return state

    # View task list by status
    elif user_input == "3":
        filter_status = input("\n🗣  Please enter the status you want to filter the tasks by? Usage: <status>, default is all\n� USER: ")
 
        filter_status = filter_status if filter_status in ["pending", "in_progress", "done"] else "all"

        get_tasks_by_status(state, filter_status)
        state.intent = "get_tasks"
        return state

    elif user_input.split(" ")[0] in ["end", "bye", "exit","quit","goodbye", "finish"]:
        print("👋 Goodbye!")
        state.intent = "end"
        return state

    else:
        print("❓ I didn't understand that. Try again.")
        state.intent = "get_tasks"
        return state


graph = StateGraph(TaskManagerState)
graph.add_node("agent", agent)
graph.set_entry_point("agent")

graph.add_conditional_edges("agent", should_continue, {
    "continue": "agent",
    "end": END,
})
app = graph.compile()


tasks_manager_state: TaskManagerState = TaskManagerState(tasks=[])
app.invoke(tasks_manager_state)
 
