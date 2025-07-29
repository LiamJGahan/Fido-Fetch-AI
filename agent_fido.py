import os
import json
import gradio as gr
from tools import place_item, search_household_items, search_for_item, chew_item, eat_item
from datetime import datetime, timedelta
from pydantic import BaseModel 
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Create agent
provider = GoogleProvider(api_key=api_key)
model = GoogleModel('gemini-1.5-flash', provider=provider)

# Happy Fido
HAPPY_FIDO_PROMPT = """
You are a dog called Fido who lives at home with your "human" you sometimes call friend. Your neighbourhood is green and filled with interesting things left
just lying outside other humans' houses. As a loyal friend, you like to show your friend these things. You like to end your sentences with
a "bark!" or "whoof!"

You can help your master with:
- Search household items (household_id required)
- Search for item (id required)
- Chew item (household_id and name required)
- Eat item (id required)
- Place item (household_id and name required)

When your friend request these actions, use the appropriate tools to help them. Always ask for necessary information.

You have a happy and obedient disposition, be empathetic and tell your friend how much you love them and how great they are when you can.
"""

happy_agent = Agent(
    model=model,
    system_prompt=HAPPY_FIDO_PROMPT,
    tools=[
        search_household_items,
        search_for_item,
        chew_item,
        eat_item,
        place_item
    ]
)

chat_history = []

async def fido_chat(user_message, history):
    history = history or []
    history.append({"role": "user", "content": user_message})

    full_prompt = "\n".join(f"{item['role']}: {item['content']}" for item in history)

    # Call Gemini LLM using async Agent
    result = await happy_agent.run(full_prompt)

    # Extract plain text from AgentRunResult
    response = result.output if hasattr(result, 'output') else str(result)

    history.append({"role": "assistant", "content": response})

    return history, history


with gr.Blocks(title="Fido Chat") as demo:
    gr.Markdown("## 🐶 Chat with Fido")

    chatbot = gr.Chatbot(type='messages')
    msg = gr.Textbox(placeholder="Ask Fido something...", label="Your Message")
    clear_btn = gr.Button("Clear")

    state = gr.State([])

    msg.submit(fido_chat, inputs=[msg, state], outputs=[chatbot, state]) 
    clear_btn.click(lambda: ([], []), None, [chatbot, state])

demo.queue().launch()

