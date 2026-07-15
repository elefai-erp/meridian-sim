"""Provider-agnostic AI adapter.

The simulation never blocks on AI availability: all AI work (appraisal
narrative, examiner interrogation, AI-usage-quality analysis) runs as queued
jobs against this interface. Hosted deployments default to Anthropic; a
self-hoster can switch provider per site:

    bench --site <site> set-config ai_provider ollama
    bench --site <site> set-config ai_model llama3.1
"""

from abc import ABC, abstractmethod


class AIAdapter(ABC):
    @abstractmethod
    def complete(self, system: str, messages: list[dict], max_tokens: int = 4096) -> str:
        """messages: [{"role": "user"|"assistant", "content": str}, ...]"""


def get_adapter() -> AIAdapter:
    import frappe

    provider = frappe.conf.get("ai_provider", "anthropic")
    if provider == "anthropic":
        from meridian_sim.ai.anthropic_driver import AnthropicAdapter

        return AnthropicAdapter(
            api_key=frappe.conf.get("anthropic_api_key"),
            model=frappe.conf.get("ai_model", "claude-sonnet-5"),
        )
    raise NotImplementedError(f"AI provider not implemented yet: {provider}")


class NullAdapter(AIAdapter):
    """Used in tests and when no provider is configured — the simulation
    proceeds; AI-dependent artifacts are queued until a provider exists."""

    def complete(self, system, messages, max_tokens=4096):
        raise RuntimeError("No AI provider configured (site config: ai_provider)")
