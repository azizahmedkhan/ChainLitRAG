import os
from openai import AsyncOpenAI  
import chainlit as cl  
from chainlit.prompt import Prompt, PromptMessage  
from chainlit.playground.providers import ChatOpenAI  
from dotenv import load_dotenv

load_dotenv()

system_template = """You are a helpful assistant who always speaks in a pleasant tone!"""
user_templere = """{input} 
Think through your response step by step"""

@cl.on_chat_start
async def start_chat():
    settings = {
        "model": "gpt-3.5-turo",
        "temperature":0,
        "max_tokens":500,
        "top_p":1,
        "frequency_penalty":0,
        "presence_penalty":0,
    }
    cl.user_session.set("settings",settings)


@cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    client = AsyncOpenAI()

    print(message.content)

    prompt = Prompt(
        provider=ChatOpenAI.id,
        messages=[
            PromptMessage(
                role="system",
                template=system_template,
                formatted=system_template,
            ),
            PromptMessage(
                role="user",
                template=user_template,
                formatted=user_template.format(input=message.content),
            ),
        ],
        inputs={"input": message.content},
        settings=settings,
    )

    print([m.to_openai() for m in prompt.messages])

    msg = cl.Message(content="")

    # Call OpenAI
    async for stream_resp in await client.chat.completions.create(
        messages=[m.to_openai() for m in prompt.messages], stream=True, **settings
    ):
        token = stream_resp.choices[0].delta.content
        if not token:
            token = ""
        await msg.stream_token(token)

    # Update the prompt object with the completion
    prompt.completion = msg.content
    msg.prompt = prompt

    # Send and close the message stream
    await msg.send()
