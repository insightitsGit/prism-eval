"""Agent adapters: sync callables, async callables, and HTTP JSON endpoints."""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import urllib.error
import urllib.request
from typing import Any, Awaitable, Callable, Dict, Mapping, MutableMapping, Optional, Union

AgentFn = Callable[[Dict[str, Any]], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]
AsyncAgentFn = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


def ensure_async_agent(agent_fn: AgentFn) -> AsyncAgentFn:
    """Wrap sync callables so the engine can always await them."""
    if inspect.iscoroutinefunction(agent_fn):
        return agent_fn  # type: ignore[return-value]

    async def _async_wrapper(input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await asyncio.to_thread(agent_fn, input_data)
        if inspect.isawaitable(result):
            return await result  # type: ignore[misc]
        if not isinstance(result, dict):
            return {"_raw": result}
        return result

    return _async_wrapper


def make_http_agent(
    url: str,
    *,
    timeout_s: float = 60.0,
    headers: Optional[Mapping[str, str]] = None,
    method: str = "POST",
) -> AsyncAgentFn:
    """
    Build an async agent that POSTs ``input_data`` as JSON to ``url``.

    Extra headers can be supplied directly or via ``PRISM_EVAL_HTTP_HEADERS``
    (JSON object). Optional bearer token via ``PRISM_EVAL_HTTP_TOKEN``.
    """
    merged: MutableMapping[str, str] = {"Content-Type": "application/json"}
    env_headers = os.environ.get("PRISM_EVAL_HTTP_HEADERS")
    if env_headers:
        parsed = json.loads(env_headers)
        if isinstance(parsed, dict):
            merged.update({str(k): str(v) for k, v in parsed.items()})
    token = os.environ.get("PRISM_EVAL_HTTP_TOKEN")
    if token:
        merged["Authorization"] = f"Bearer {token}"
    if headers:
        merged.update(dict(headers))

    async def http_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
        def _request() -> Dict[str, Any]:
            req = urllib.request.Request(
                url,
                data=json.dumps(input_data).encode("utf-8"),
                headers=dict(merged),
                method=method.upper(),
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"HTTP agent {method.upper()} {url} failed: {exc.code} {body}"
                ) from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(f"HTTP agent request failed: {exc}") from exc
            if not isinstance(payload, dict):
                raise TypeError("HTTP agent must return a JSON object")
            return payload

        return await asyncio.to_thread(_request)

    return http_agent


async def identity_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Empty extraction reference agent (demonstrates FAIL path)."""
    _ = input_data
    return {}


def load_agent_callable(dotted_path: Optional[str]) -> AgentFn:
    """
    Load an agent callable.

    Formats:
      - ``module.path:function`` (sync or async)
      - ``http://...`` / ``https://...`` JSON endpoint
      - omitted → identity_agent
    """
    if not dotted_path:
        return identity_agent

    if dotted_path.startswith("http://") or dotted_path.startswith("https://"):
        return make_http_agent(dotted_path)

    if ":" not in dotted_path:
        raise ValueError(
            "agent path must look like 'package.module:callable' or an http(s) URL"
        )

    module_name, attr = dotted_path.split(":", 1)
    import importlib

    module = importlib.import_module(module_name)
    fn = getattr(module, attr)
    if not callable(fn):
        raise TypeError(f"{dotted_path} is not callable")
    return fn  # type: ignore[return-value]
