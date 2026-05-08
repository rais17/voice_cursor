from pydantic import BaseModel
from typing import List
from langchain_core.messages import BaseMessage

# equivalent of MessagesAnnotation state
class AgentState(BaseModel):
    messages: List[BaseMessage] = []