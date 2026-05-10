from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from src.config import chat_model, mongo_client
from src.tools import tools
from src.prompt.system_prompt import get_system_prompt
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.mongodb import MongoDBSaver


def create_voice_agent():
    tool_node = ToolNode(tools)
    model = chat_model.bind_tools(tools)

    def llm_node(state: MessagesState):
        messages = [SystemMessage(content=get_system_prompt())] + state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("llm_node", llm_node)
    workflow.add_node("tools", tool_node)
    workflow.add_edge(START, "llm_node")
    workflow.add_conditional_edges("llm_node", tools_condition)
    workflow.add_edge("tools", "llm_node")

    checkpointer = MongoDBSaver(mongo_client, db_name="voice_cursor")
    return workflow.compile(checkpointer=checkpointer)


voice_agent = create_voice_agent()