from pathlib import Path

from fastmcp import Client
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

# The MCP server: tools.py is launched as its own process and spoken to over MCP
TOOLS_PATH = Path(__file__).parent / "tools.py"


class InsuranceAgent:
    def __init__(self):
        # Initialize the Local LLM Brain (ollama qwen 2.5:3b)
        self.llm = ChatOllama(model="qwen2.5:3b", temperature=0)

        # Short-term memory (conversation history)
        self.chat_history = [
            SystemMessage(content=(
                "You are an expert UK InsurTech AI claims assistant. "
                "You operate strictly within the domain of UK insurance. "
                "If a user asks about unrelated topics (such as cooking, recipes, general trivia, or external programming), "
                "politely decline and redirect them back to their insurance policy or claim.\n\n"
                "TOOL RULES:\n"
                "1. If the user gives a policy ID AND a claim or repair amount, call calculate_payout with both values. "
                "Do not call verify_policy first, because calculate_payout already verifies the policy.\n"
                "2. If the user gives only a policy ID with no amount, call verify_policy.\n"
                "3. After a tool returns a result, reply using only that result. "
                "If a payout was calculated, always state the final payout amount in pounds and the deductible.\n"
                "4. If the policy is expired or not found, say so clearly and do not mention a payout."
            ))
        ]

    async def process_claim(self, user_input: str) -> str:
        """ReAct loop over MCP: User Input -> LLM Reason -> MCP Tool Call -> Observation -> Final Response."""

        self.chat_history.append(HumanMessage(content=user_input))

        # Connect to the MCP server (tools.py) as an MCP client
        async with Client(TOOLS_PATH) as client:

            # Discover the tools from the server over MCP
            mcp_tools = await client.list_tools()
            tool_specs = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": getattr(tool, "input_schema", None) or tool.inputSchema,                    },
                }
                for tool in mcp_tools
            ]
            llm_with_tools = self.llm.bind_tools(tool_specs)

            # First LLM call: it may reply directly or request a tool
            response = await llm_with_tools.ainvoke(self.chat_history)
            self.chat_history.append(response)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    print(f"\n[Agent Action] LLM decided to call MCP tool: '{tool_name}' with args: {tool_args}")

                    # Execute the tool through the MCP protocol
                    try:
                        result = await client.call_tool(tool_name, tool_args)
                        tool_result = result.data if result.data is not None else str(result.content)
                    except Exception as e:
                        tool_result = {"status": "Error", "message": str(e)}

                    print(f"[Tool Observation] Result: {tool_result}")

                    self.chat_history.append(
                        ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
                    )

                # Second LLM call: write the final answer using the tool results
                final_response = await llm_with_tools.ainvoke(self.chat_history)
                self.chat_history.append(final_response)
                return final_response.content

            return response.content


# Simple interactive CLI test if run directly
if __name__ == "__main__":
    import asyncio

    agent = InsuranceAgent()
    print(" The Insurance Claims Agent initialized! (Type 'exit' to quit)\n")

    while True:
        query = input("User Claim: ")
        if query.lower() in ["exit", "quit"]:
            break

        answer = asyncio.run(agent.process_claim(query))
        print(f"\nAgent Response:\n{answer}\n" + "-" * 50)