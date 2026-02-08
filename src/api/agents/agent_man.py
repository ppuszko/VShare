import asyncio 
from typing import AsyncGenerator

from fastapi import Request

from langchain.messages import HumanMessage



class AgentManager:
    def __init__(self, agent):
        self._agent = agent
        self._lock = asyncio.Lock()

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async with self._lock:
            try:
                async for chunk in self._agent.astream({"messages":[HumanMessage(content=prompt)]}):
                    if "actions" in chunk:
                        yield f"{chunk['actions'][0].log}\n\n" 
                    elif "steps" in chunk:
                        yield f"{chunk['steps'][0].observation}\n\n"
                    elif "output" in chunk:
                        yield f"{chunk['output'][0]}\n\n"
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"


def get_agent_man(request: Request) -> AgentManager:
    return request.app.state.agent_man