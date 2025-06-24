from typing import Annotated, Sequence, TypedDict, Literal, List
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage  
from langchain_core.messages import ToolMessage  
from langchain_core.messages import SystemMessage  
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import os
import uuid

load_dotenv()

##### State Management #####
class Task(TypedDict):
    """
    Represents a task to manager agent.
    """
    task_id: str
    priority: int
    description: str
    status: Literal["pending", "in_progress", "done"]  


class TaskManagerState(TypedDict):
    """
    Represents the list of tasks to manager agent.
    """
    tasks: list[Task]

    def get_tasks(self, task_ids: list[str]) -> list[Task]:
        return [task for task in self['tasks'] if task['task_id'] in task_ids]
 


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

##### Tools Implementation #####
@tool
def add_task(priority: int, description: str):
    """
    Add a new task to the task manager.
    """
    new_task = Task(
        task_id=str(uuid.uuid4()), 
        priority=priority, 
        description=description, 
        status="pending"
    )
    tasks_manager_state['tasks'].append(new_task)


@tool
def complete_tasks(task_ids: List[str]):
    """
    Complete a task in the task manager.
    """
    print(f"Complete Node: value is now {tasks_manager_state['tasks']}")
    for task in tasks_manager_state['tasks']:
        if task['task_id'] in task_ids:
            task['status'] = "done" 


@tool
def get_tasks_by_status(
    status: Literal["pending", "in_progress", "done"]):
    """
    Get tasks by status.
    """
    print(f"Get Tasks Node: value is now {tasks_manager_state['tasks']}")
    
    tasks_manager_state['tasks'] = [task for task in tasks_manager_state['tasks'] if task['status'] == status]


##### Graph Architecture #####


def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

def agent_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
        You are task manager, a helpful task manager. You are going to help the user update and modify tasks.
        - If the user wants to add a new task, use the 'add_task' tool.
        - If the user wants to complete a task, you need to use the 'complete_tasks' tool.
        - If the user wants to get tasks by status, you need to use the 'get_tasks_by_status' tool.
    
        The current task content is:{tasks_manager_state['tasks']}
        """)
    if not state["messages"]:
        user_input = "No tasks found, please add a task"
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input(f"\nCurrently there are '{len(tasks_manager_state['tasks'])}' tasks, \nDo you want to add a new task or complete a task?")
        print(f"\n� USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)
    
    print(f"\n� AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"� USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")
    return {"messages": list(state["messages"]) + [user_message, response]}


def should_continue(state: AgentState) -> str:
    """
    Determine if the agent should continue or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


tasks_manager_state = TaskManagerState(tasks=[])

tools = [add_task, complete_tasks, get_tasks_by_status]
model = ChatOpenAI(model = "gpt-4o", api_key=os.getenv("OPENAI_API_KEY")).bind_tools(tools)


graph = StateGraph(AgentState)
graph.add_node("agent", agent_call)
graph.add_node("tools", ToolNode(tools=tools))

graph.set_entry_point("agent")

graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END,
    },
)
app = graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()



# inputs = {"messages": [("user", "add a task with priority 1 and description 'buy groceries'")]}

# res = app.invoke(inputs)

# print(res)
# print(tasks_manager_state['tasks'])