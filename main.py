from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agent import InsuranceAgent

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise Insurance Claims MCP Agent API",
    description="An autonomous local AI agent backend powered by FastMCP, Ollama (qwen2.5:3b), and Pydantic for UK insurance claims and payout reconciliation.",
    version="1.0.0"
)

# Initialize the agent instance globally so it maintains session memory
agent = InsuranceAgent()

# Define Pydantic request schema
class ClaimRequest(BaseModel):
    claim_text: str = Field(
        description="The natural language insurance claim submitted by the client.",
        example="Hi, I need to file a claim for policy POL-UK-0001 with a repair cost of £1,200."
    )

class ClaimResponse(BaseModel):
    status: str
    response: str

@app.get("/", tags=["Health Check"])
def health_check():
    """Confirms that the Insurance Claims MCP Agent API is running."""
    return {
        "status": "Online",
        "service": "UK InsurTech Claims Agent API",
        "model": "qwen2.5:3b via Ollama"
    }

@app.post("/claims/process", response_model=ClaimResponse, tags=["Agent Operations"])
async def process_insurance_claim(payload: ClaimRequest):
    """
    Receives a natural language claim, runs the agent ReAct loop (reasoning, tool-calling, 
    policy verification, and deductible calculation), and returns a grounded response.
    """
    try:
        agent_answer = await agent.process_claim(payload.claim_text)
        return {
            "status": "Success",
            "response": agent_answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)