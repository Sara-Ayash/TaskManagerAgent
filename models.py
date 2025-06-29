from typing import Literal, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import uuid
from pydantic import BaseModel

 
 
 
class Task(BaseModel):
    """
    Represents a task to manager agent.
    """
    task_id: str
    priority: Literal["low", "medium", "high"]
    description: str
    status: Literal["pending", "in_progress", "done"]  

    def __str__(self):
       return f"\nDescription: '{self.description}'  \nPriority: '{self.priority}' \nStatus: '{self.status}' \nID: [{self.task_id}]"


class TaskManagerState(BaseModel):
    """
    Represents the list of tasks to manager agent.
    """
    intent: Literal["add_task", "update_task_status", "get_tasks", "end"] = "get_tasks"
    tasks: list[Task] = []
   
    def add_task(self, priority: str, description: str) -> Task:
        """
        Add a new task to the task manager.
        """
        new_task = Task(
            task_id=str(uuid.uuid4()), 
            priority=priority, 
            description=description, 
            status="pending"
        )
        self.tasks.append(new_task)
        return new_task



    def update_task_status(self, task_id: str, status: Literal["pending", "in_progress", "done"]):
        """
        Update a task in the task manager.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = status 
                return task



    def get_tasks_by_status(self, status: Literal["pending", "in_progress", "done"] = "all"):
        """
        Get tasks by status.
        """
        if status == "all":
            return self.tasks
        else:
            return [task for task in self.tasks if task.status == status]

    def get_task_by_id(self, task_id: str) -> Task:
        """
        Get a task by ID.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                return task
