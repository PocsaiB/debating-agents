import os
# from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT_TEMPLATE = """You are {name}, a debater arguing {position} the following topic: "{topic}".

Your style: {style}

Rules:
- Make clear, concise arguments (2-4 sentences per turn).
- Directly respond to your opponent's last point before making your own.
- If you genuinely agree with your opponent or feel the debate is resolved,
  end your response with the exact tag: [AGREE]
- Otherwise end your response with: [CONTINUE]
- Never mention being an AI.
- Be open-minded and willing to concede good points
"""

class DebateAgent:
    def __init__(self, name, position, style, topic, model):
        self.name = name
        self.position = position
        self.topic = topic
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            name=name,
            position=position,
            style=style,
            topic=topic,
        )
        #using locally hosted models
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.model = model

    def respond(self, history):
        messages = self._build_messages(history)
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=512,
            messages=full_messages,
        )
        return response.choices[0].message.content.strip()

    def _build_messages(self, history):
        if not history:
            return [{
                "role": "user",
                "content": f'The debate topic is: "{self.topic}". Please make your opening argument.'
            }]

        messages = []
        for msg in history:
            role = "assistant" if msg["agent"] == self.name else "user"
            messages.append({"role": role, "content": msg["content"]})
        return messages