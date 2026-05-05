
from agent.llm import get_llm

from contextlib import asynccontextmanager
from agent.mcp_client import get_mcp_config
from langchain.agents import create_agent

from langchain_mcp_adapters import MultiServerMCPClient

@asynccontextmanager
async def build_agent(thinking:bool=True):

    llm = get_llm(thinking=thinking)

    async with MultiServerMCPClient(get_mcp_config()) as client:
        tools = client.get_tools()
        

        agent = create_agent(model=llm, tools=tools)
        yield agent
    

