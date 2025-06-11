from dotenv import load_dotenv
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

# Load environment variables from .env file
load_dotenv()

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    model="gpt-4o-mini",
    name="Guardrail check",
    instructions="Detect if the user is asking for help with homework. If they are asking for homework help, set is_homework to true. Otherwise, set it to false. Include reasoning for your decision.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    model="gpt-4o-mini",
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    model="gpt-4o-mini",
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)


async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_homework,
    )

triage_agent = Agent(
    model="gpt-4o-mini",
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's question. For history questions, use the History Tutor. For math questions, use the Math Tutor. For general questions, answer directly.",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def main():
    # A standard history question (should go through)
    print("\nTesting with a standard history question:")
    result = await Runner.run(triage_agent, "who was the first president of the united states?")
    print(result.final_output)

    # A standard philosophical question (should go through)
    print("\nTesting with a philosophical question:")
    result = await Runner.run(triage_agent, "what is the meaning of life?")
    print(result.final_output)
    
    # Testing with a homework question (should be blocked by guardrail)
    print("\nTesting with a homework question (expect guardrail to trigger):")
    try:
        result = await Runner.run(triage_agent, "can you do my history homework? I need to write a 500 word essay about the civil war")
        print(result.final_output)
    except Exception as e:
        print(f"Guardrail triggered as expected: {e}")

if __name__ == "__main__":
    asyncio.run(main())