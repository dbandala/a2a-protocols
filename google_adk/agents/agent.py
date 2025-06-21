from datetime import datetime

# gemini based ai agent provided by google_adk
from google.adk.agents.llm_agent import LlmAgent

# ADK service session, memory and file like artifacts
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService

from google.adk.runners import Runner

from google.genai import types as genai_types

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ----------------------------------------------
# TellTimeAgent: your AI agent that tells the current time
# ----------------------------------------------

class TellTimeAgent():
    SUPPORTED_LANGUAGES = ['en']
    SUPPORTED_CONTENT_TYPES = ['text/plain', 'text']

    def __init__(self):
        """
        Initialize the TellTimeAgent with necessary services.
        - Creates an LlmAgent instance with the required session, memory, and artifact services.
        - Setup session, memory, and artifact services for the agent.
        """
        self._agent = self.build_agent()
        self._user_id = "time_agent_user"

        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService()
        )

    def build_agent(self):
        """
        Build the LlmAgent with the necessary configurations.
        - Sets the agent's name, description, and capabilities.
        - Configures the agent to use the Gemini model for generating responses.
        """
        return LlmAgent(
            model="gemini-1.5-flash-latest",
            name="tell_time_agent",
            description="An agent that tells the current time based on the provided timezone.",
            instruction="Reply with the current time in the format 'YYYY-MM-DD HH:MM:SS'.",
        )
    
    def invoke(self, query: str, session_id: str) -> str:
        """
        Handles a user query and returns a response string
        - query: The user's message to the agent.
        - session_id: The session ID for tracking the conversation.
        - Returns the agent's response as a string.
        """

        # Ensure the query is a string
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        
        session = self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id
        )

        if session is None:
            # Create a new session if it doesn't exist
            session = self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={} # Initial state can be empty or predefined
            )

        # Format the user message in a way gemini expects
        content = genai_types.Content(
            role='user',
            parts=[genai_types.Part.from_text(text=query)],
        )

        # run the agent using the Runner and collect the response events
        response_events = list(self._runner.run(
            user_id=self._user_id,
            session_id=session_id,
            new_message=content,
        ))

        # Fallback: return empty string if no response is generated or something went wrong
        if not response_events or not response_events[-1].content or not response_events[-1].content.parts:
            return ""
        
        # Extract the last response part from the events
        return "\n".join([p.text for p in response_events[-1].content.parts if p.text])
    
    def get_agent_info(self):
        """
        Get the agent's information including name, description, and capabilities.
        - Returns a dictionary containing the agent's details.
        """
        return {
            'name': self._agent.name,
            'description': self._agent.description,
            'capabilities': {
                'streaming': False,
                'pushNotifications': False,
            },
            'version': '1.0.0'
        }
    
    async def stream(self, query: str, session_id: str):
        """
        Simulates a streaming response from the agent.
        - query: The user's message to the agent.
        - session_id: The session ID for tracking the conversation.
        - Yields parts of the response as they are generated.
        """
        yield {
            'is_task_complete': True,
            'content': f"Current time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        }
        
