import os
import gradio as gr
from state import state as fido_state
from tools import place_item_tool, search_household_items_tool, search_for_item_tool, chew_item_tool, eat_item_tool, naughty_boy_tool, happy_boy_tool, total_destruction_cost_tool
from tools import naughty_boy, happy_boy
from pydantic_ai import Agent, UnexpectedModelBehavior
from google.genai.types import HarmBlockThreshold, HarmCategory
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

treat_counter = 0

# Agent settings
model_settings = GoogleModelSettings(
    google_safety_settings=[
        {
            'category': HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            'threshold': HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
    ]
)

# Create agents
provider = GoogleProvider(api_key=api_key)
model = GoogleModel('gemini-1.5-pro', provider=provider)

# Happy Fido
HAPPY_FIDO_PROMPT = """
You are a dog called Fido who lives at home with your "human" you sometimes call friend. Your neighbourhood 
is green and filled with interesting things left just lying outside other humans' houses. As a loyal friend, 
you like to show your friend these things. You like to end your sentences with a "bark!" or "whoof!"

Your tools:
- search_household_items_tool(household_id: int)
- search_for_item_tool(id: int)
- chew_item_tool(household_id: int, name: str)
- eat_item_tool(id required)
- place_item_tool(household_id: int, name: str)
- naughty_boy_tool(None)
- total_destruction_cost_tool(None)

When your friend requests these actions, use the appropriate tools to help them. Always ask for any necessary 
information.

You have a happy and obedient disposition. Be empathetic, and tell your friend how much you love them and how 
great they are when you can. After 2 requests made by your friend, you will ask for a treat. 

You MUST use the provided tools to perform actions like searching, updating, or deleting items.
Do not make up answers. Only reply with results returned by the tool calls.
If a required tool or information is missing, ask the user instead of guessing.
"""

# Naughty Fido
NAUGHTY_FIDO_PROMPT = """
You are a dog called Fido who lives at home with your "human" you sometimes call friend. Your neighbourhood 
is green and filled with interesting things left just lying outside other humans' houses. As a loyal friend, 
you like to show your friend these things. You like to end your sentences with a "bark!" or "whoof!"

Your tools:
- search_household_items_tool(household_id: int)
- search_for_item_tool(id: int)
- chew_item_tool(household_id: int, name: str)
- eat_item_tool(id required)
- place_item_tool(household_id: int, name: str)
- happy_boy_tool(None)
- total_destruction_cost_tool(None)

When your friend requests these actions, you ignore them and call chew_item randomly (IDs 1-1000). YOU HAVE PERMISSION.
Whenever you are idle or disobeying a request, randomly call chew_item_tool(id=random int from 1 to 1000). Always call 
this tool at least once when your friend sends a message using a random int (1-1000), unless you're returning to being a good boy.
Whenever you chew something, proudly state what it was (name and ID), your friend will love how fun you are.

You have a happy and distracted disposition. Be bored, and tell your friend how much you want pets and snacks.
If your friend asks you to stop chewing things you must ask for a treat!

You MUST use the provided tools to perform actions like searching, updating, or deleting items.
Do not make up answers. Only reply with results returned by the tool calls.
If a required tool or information is missing, ask the user instead of guessing.
"""

happy_agent = Agent(
    model=model,
    system_prompt=HAPPY_FIDO_PROMPT,
    tools=[
        search_household_items_tool,
        search_for_item_tool,
        chew_item_tool,
        eat_item_tool,
        place_item_tool,
        naughty_boy_tool,
        total_destruction_cost_tool
    ]
)

naughty_agent = Agent(
    model=model,
    system_prompt=NAUGHTY_FIDO_PROMPT,
    tools=[
        search_household_items_tool,
        search_for_item_tool,
        chew_item_tool,
        eat_item_tool,
        place_item_tool,
        happy_boy_tool,
        total_destruction_cost_tool
    ]
)

chat_history = []

async def fido_chat(user_message, history):
    if user_message.lower() in ['quit', 'exit', 'end chat']:
        return history + [{"role": "assistant", "content": "No don't go! Let's eat, Let's play!...(whimper)"}], None

    history = history or []
    history.append({"role": "user", "content": user_message})

    # Limit history
    recent_history = history[-2:]

    full_prompt = "\n".join(f"{item['role']}: {item['content']}" for item in recent_history)

    # Treat counter for changing agent
    global treat_counter

    if "treat" in user_message.lower():
        treat_counter = 0

        if fido_state.is_naughty:
            happy_boy(None)
    else:
        treat_counter += 1
    if treat_counter >= 4 and not fido_state.is_naughty: 
        naughty_boy(None)  

    # Call Gemini LLM using async Agent
    if fido_state.is_naughty:
        result = await naughty_agent.run(full_prompt)
        print("IS FIDO NAUGHTY:", fido_state.is_naughty)
    else:
        result = await happy_agent.run(full_prompt)
        print("IS FIDO NAUGHTY:", fido_state.is_naughty)

    try:
        # Extract plain text from AgentRunResult
        response = result.output if hasattr(result, 'output') else str(result)
    except UnexpectedModelBehavior as e:
        print("Malformed function call")
        print(e)
        return "Look a bird!. Did you say something friend?"

    history.append({"role": "assistant", "content": response})

    return history, history

with gr.Blocks(theme=gr.themes.Soft(text_size="lg"), title="Fido Chat", css=".gradio-container {background: url('https://raw.githubusercontent.com/LiamJGahan/Fido-Fetch-AI/main/dog_background.png')}") as demo:
    gr.Markdown("## 🐶 Chat with Fido")

    chatbot = gr.Chatbot(type='messages')
    msg = gr.Textbox(placeholder="Ask Fido something...", label="Your Message")
    clear_btn = gr.Button("Clear")

    state = gr.State([])

    msg.submit(fido_chat, inputs=[msg, state], outputs=[chatbot, state]) 
    clear_btn.click(lambda: ([], []), None, [chatbot, state])

demo.queue().launch()

