import asyncio
import os
from dotenv import load_dotenv
from pydantic import SecretStr

# Browser-use and LangChain imports
from browser_use import Agent, Browser, BrowserConfig
from langchain_groq import ChatGroq

load_dotenv()

BASE_URL = os.getenv("FLASK_BASE_URL", "http://127.0.0.1:5000")

def get_llm():
    """Configures Groq as the brain."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in .env")
    
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        api_key=SecretStr(api_key),
        temperature=0.0
    )

async def run_task(task: str, headless: bool = False) -> str:
    """
    Executes the task using Groq + Browser-Use.
    Configured specifically for text-only LLMs.
    """
    llm = get_llm()
    
    # Create the browser object separately to avoid the 'browser_config' error
    browser = Browser(
        config=BrowserConfig(
            headless=headless,
            disable_security=True
        )
    )

    full_task = (
        f"Go to {BASE_URL}. Your task: {task}. "
        "Interact with the web page elements by their labels or text. "
        "Once you see a success message or flash message, describe what it says and finish."
    )

    # Initialize the Agent
    agent = Agent(
        task=full_task,
        llm=llm,
        browser=browser,
        use_vision=False # CRITICAL: Groq is text-only, so we turn off Vision
    )

    print(f"\n[AI Agent] Reasoning with Llama 3.3 (Text-Only Mode)...")
    
    try:
        history = await agent.run(max_steps=15)
        result = history.final_result()
        return str(result) if result else "Agent reached the end of the action sequence."
    except Exception as e:
        return f"Agent Execution Error: {str(e)}"
    finally:
        await browser.close()

def run(task: str, headless: bool = False) -> str:
    """Entry point for the demo script."""
    return asyncio.run(run_task(task, headless=headless))