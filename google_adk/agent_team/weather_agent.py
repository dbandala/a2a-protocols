#!/usr/bin/env python3
"""
Weather Agent Script
Converted from weather_agent.ipynb

This script creates a weather agent using Google ADK that can provide weather information
for specific cities using a mock weather database.
"""

import os
import asyncio
import subprocess
import sys
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()


def install_dependencies():
    """Install required packages if not already installed."""
    try:
        import google.adk
        import litellm
        print("Dependencies already installed.")
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-adk", "-q"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "litellm", "-q"])
        print("Installation complete.")


# --- Define Model Constants for easier use ---

# More supported models can be referenced here: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# More supported models can be referenced here: https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
MODEL_GPT_4O_MINI = "openai/gpt-4o-mini"  # You can also try: gpt-4.1-mini, gpt-4o etc.

# More supported models can be referenced here: https://docs.litellm.ai/docs/providers/anthropic
MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514"  # You can also try: claude-opus-4-20250514 , claude-3-7-sonnet-20250219 etc


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")  # Log tool execution
    city_normalized = city.lower().replace(" ", "")  # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


def create_weather_agent():
    """Create and configure the weather agent."""
    # Use one of the model constants defined earlier
    AGENT_MODEL = MODEL_GPT_4O_MINI  # Starting with GPT-4o-mini

    weather_agent = Agent(
        name="weather_agent_v1",
        model=AGENT_MODEL,  # Can be a string for Gemini or a LiteLlm object
        description="Provides weather information for specific cities.",
        instruction="You are a helpful weather assistant. "
                    "When the user asks for the weather in a specific city, "
                    "use the 'get_weather' tool to find the information. "
                    "If the tool returns an error, inform the user politely. "
                    "If the tool is successful, present the weather report clearly.",
        tools=[get_weather],  # Pass the function directly
    )

    print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")
    return weather_agent


async def setup_session_and_runner(weather_agent):
    """Setup session service and runner for the weather agent."""
    # --- Session Management ---
    # Key Concept: SessionService stores conversation history & state.
    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    session_service = InMemorySessionService()

    # Define constants for identifying the interaction context
    APP_NAME = "weather_tutorial_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=weather_agent,  # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service  # Uses our session manager
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    
    return runner, session_service, session


async def main():
    """Main function to demonstrate the weather agent."""
    print("Libraries imported.")
    print("\nEnvironment configured.")
    
    # Test the get_weather tool
    print("\n--- Testing get_weather tool ---")
    print(get_weather("New York"))
    print(get_weather("Paris"))
    
    # Create the weather agent
    print("\n--- Creating Weather Agent ---")
    weather_agent = create_weather_agent()
    
    # Setup session and runner
    print("\n--- Setting up Session and Runner ---")
    runner, session_service, session = await setup_session_and_runner(weather_agent)
    
    print("\n--- Weather Agent Setup Complete ---")
    print("The weather agent is now ready to use!")
    print("You can interact with the agent using the runner object.")
    
    # Example of how to use the agent (commented out for now)
    # user_message = "What's the weather like in Tokyo?"
    # response = await runner.run(user_id="user_1", session_id="session_001", message=user_message)
    # print(f"Agent response: {response}")


if __name__ == "__main__":
    # Install dependencies if needed
    install_dependencies()
    
    # Run the main function
    asyncio.run(main())
