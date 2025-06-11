from dotenv import load_dotenv
load_dotenv()

from agents import Agent

history_tutor_agent = Agent(
    model="gpt-4o-mini",
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    model="gpt-4o-mini",
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

triage_agent = Agent(
    model="gpt-4o-mini",
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)

from agents import Runner

async def main():
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# This code defines a simple triage agent that routes questions to either a history tutor or a math tutor based on the question type.
# The triage agent uses the `handoffs` feature to delegate questions to specialized agents.