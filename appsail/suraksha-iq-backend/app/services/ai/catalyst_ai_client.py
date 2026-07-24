"""
Catalyst AI Client

Reusable client for interacting with Zoho Catalyst AI.
"""

from typing import Any, Dict, List, Optional

from app.config.settings import settings
from app.core.catalyst import catalyst_manager
from app.core.exceptions import RepositoryError
from app.core.logger import logger
from zcatalyst_sdk.exceptions import CatalystError


class CatalystAIClient:
    """Thin wrapper around Zoho Catalyst AI."""

    def __init__(self, request: Any) -> None:
        self.request = request
        self.app = catalyst_manager.get_app(request)

    async def generate_completion(
        self,
        *,
        model: Optional[str] = None,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call Catalyst AI for a structured completion."""
        try:
            payload: Dict[str, Any] = {
                "model": model or settings.ai_model,
                "messages": messages,
                "temperature": temperature if temperature is not None else settings.ai_temperature,
                "max_tokens": max_tokens if max_tokens is not None else settings.ai_max_tokens,
            }
            if response_format:
                payload["response_format"] = response_format

            endpoint = self._resolve_endpoint()
            logger.info(f"Calling Catalyst AI at {endpoint}")

            # Use Catalyst SDK HTTP client when available.
            response = self._call_catalyst_api(endpoint, payload)
            return _normalize_ai_response(response)

        except CatalystError as e:
            logger.error(f"Catalyst AI request failed: {e}")
            raise RepositoryError(f"Catalyst AI request failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected AI client error: {e}")
            raise RepositoryError(f"Unexpected AI client error: {e}") from e

    def _resolve_endpoint(self) -> str:
        base = settings.ai_base_url
        if base:
            return f"{base.rstrip('/')}/chat/completions"
        # Default Catalyst AI route within the same project/app.
        return "/api/v1/ai/chat/completions"

    def _call_catalyst_api(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from zcatalyst_sdk.zia import AuthorizedHttpClient
            client = AuthorizedHttpClient(self.app)
            resp = client.request("POST", path=endpoint, json=payload)
            return resp.json() if hasattr(resp, "json") else resp
        except Exception as e:
            logger.warning(f"Catalyst SDK AI path failed, falling back to std http: {e}")
            raise

    @staticmethod
    def is_configured() -> bool:
        return bool(settings.ai_api_key) or bool(settings.ai_base_url)


def _normalize_ai_response(response: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(response.get("choices"), list) and response["choices"]:
        choice = response["choices"][0]
        message = choice.get("message", {})
        return {
            "content": message.get("content", ""),
            "model": response.get("model"),
            "usage": response.get("usage", {}),
            "raw": response,
        }
    return {"content": str(response), "model": None, "usage": {}, "raw": response}
