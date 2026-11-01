import asyncio
from fastmcp import Client

async def main():
    client = Client("tools.py")
    async with client:
        tools = await client.list_tools()
        print("Tools found over MCP:")
        for tool in tools:
            print(" -", tool.name)

        result = await client.call_tool(
            "calculate_payout",
            {"policy_id": "POL-UK-0001", "claim_amount": 1200},
        )
        print("Result:", result.data)

asyncio.run(main())