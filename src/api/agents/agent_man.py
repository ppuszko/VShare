from typing import AsyncGenerator

from fastapi.requests import Request

from langchain.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain.agents import create_agent

from src.core.config.agent import AgentConfig

class AgentManager:
    def __init__(self, agent):
        self._agent = agent

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        print("DEBUG: Starting LangChain astream...")
        try:
            async for event in self._agent.astream_events({"messages":[HumanMessage(content=prompt)]}):
                if event["event"] == "on_chat_model_stream":
                    print(f"DEBUG: Yielding chunk")
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
        finally:
            print("DEBUG: Releasing lock.")


def init_agent_man(tools: list[BaseTool], request: Request) -> AgentManager:
    return AgentManager(
        agent=create_agent(
            model=request.app.state.agent_model,
            system_prompt=AgentConfig.system_prompt,
            tools=tools
        )
    )  

