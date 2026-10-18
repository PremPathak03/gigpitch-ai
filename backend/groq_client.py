import os
import json
from typing import AsyncGenerator
from groq import Groq
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT, TONE_INSTRUCTIONS, FEW_SHOT_EXAMPLE

load_dotenv()

DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")


def get_groq_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not configured.")
    return Groq(api_key=api_key)


async def generate_proposal_stream(
    job_description: str,
    skills: str,
    tone: str = "professional"
) -> AsyncGenerator[str, None]:
    """
    Streams a tailored proposal from Groq using an open-weight model.
    Yields Server-Sent Events (SSE) lines formatted as:
      data: {"text": "chunk"}\n\n
      data: {"done": true}\n\n
    """
    try:
        client = get_groq_client()
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    tone_note = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["professional"])
    full_system = f"{SYSTEM_PROMPT.format(tone=tone_note)}\n\nReference Quality Example:\n{FEW_SHOT_EXAMPLE}"

    user_prompt = f"""Here is the client's job posting:
---
{job_description.strip()}
---

Here is my freelancer skillset & background:
---
{skills.strip()}
---

Please draft the proposal now:"""

    try:
        stream = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=0.7,
            max_tokens=600,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                text_part = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'text': text_part})}\n\n"

        yield f"data: {json.dumps({'done': True, 'model': DEFAULT_MODEL})}\n\n"

    except Exception as err:
        yield f"data: {json.dumps({'error': str(err)})}\n\n"
