from dotenv import load_dotenv

from agents import Agent, Runner

# Load environment variables from .env file
load_dotenv()

agent = Agent(
    model="gpt-4o-mini",
    name="Assistant",
    instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.