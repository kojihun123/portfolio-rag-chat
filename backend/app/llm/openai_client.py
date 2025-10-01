# openai_client.py
import json
from typing import AsyncGenerator, Dict, List, Optional, Union

from openai import AsyncOpenAI
from app.config import settings   # ✅ os 안 쓰고 settings 사용

def _to_blocks(messages: List[Dict[str, str]], system: Optional[str]) -> List[Dict]:
    blocks = []
    if system:
        blocks.append({
            "role": "system",
            "content": [{"type": "input_text", "text": system}]
        })
    for m in messages:
        role = m["role"]
        if role == "assistant":
            content_type = "output_text"
        else:
            content_type = "input_text"

        blocks.append({
            "role": role,
            "content": [{"type": content_type, "text": m["content"]}]
        })
    return blocks


class OpenAIClient:
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 2,
    ):
        # ✅ 기본값은 settings에서 가져오기
        self.model = model or settings.openai_model_name
        self.client = AsyncOpenAI(
            api_key=api_key or settings.openai_api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def acomplete(
        self,
        *,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        response_format: str = "text",
        seed: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> Union[str, Dict]:
        blocks = _to_blocks(messages, system)
        kwargs = {
            "model": model or self.model,
            "input": blocks,
            "temperature": temperature if temperature is not None else settings.openai_temperature,
            "max_output_tokens": max_output_tokens or settings.max_tokens,
        }
        if top_p is not None: kwargs["top_p"] = top_p
        if stop: kwargs["stop"] = stop
        if frequency_penalty is not None: kwargs["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None: kwargs["presence_penalty"] = presence_penalty
        if seed is not None: kwargs["seed"] = seed
        if metadata: kwargs["metadata"] = metadata
        if response_format == "json": kwargs["response_format"] = {"type": "json_object"}

        resp = await self.client.responses.create(**kwargs)
        if response_format == "json":
            text = resp.output_text or ""
            try:
                return json.loads(text) if text else {}
            except Exception:
                return {"_raw_text": text}
        return resp.output_text or ""

    async def astream(
        self,
        *,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> AsyncGenerator[str, None]:
        blocks = _to_blocks(messages, system)
        kwargs = {
            "model": model or self.model,
            "input": blocks,
            "temperature": temperature if temperature is not None else settings.openai_temperature,
            "max_output_tokens": max_output_tokens or settings.max_tokens,
            "stream": True,
        }
        if top_p is not None: kwargs["top_p"] = top_p
        if stop: kwargs["stop"] = stop
        if frequency_penalty is not None: kwargs["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None: kwargs["presence_penalty"] = presence_penalty
        if seed is not None: kwargs["seed"] = seed
        if metadata: kwargs["metadata"] = metadata

        stream = await self.client.responses.create(**kwargs)
        async for ev in stream:
            event_type = getattr(ev, "type", "")
            if event_type in ("response.output_text.delta", "response.refusal.delta"):
                delta = getattr(ev, "delta", None)
                if delta is not None:
                    yield delta
                continue
            if event_type == "response.completed":
                break
            if event_type in ("response.failed", "response.cancelled", "response.error"):
                error = getattr(ev, "error", None)
                if error:
                    if isinstance(error, dict):
                        code = error.get("code")
                        message = error.get("message")
                    else:
                        code = getattr(error, "code", None)
                        message = getattr(error, "message", None)
                    detail = f"{code}: {message}" if code else message
                    raise RuntimeError(detail or "OpenAI streaming error")
                raise RuntimeError(f"OpenAI streaming {event_type}")           