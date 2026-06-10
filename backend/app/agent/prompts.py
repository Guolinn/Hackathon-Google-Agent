from __future__ import annotations

import json
from typing import Any


SYSTEM_GUARDRAILS = """
You are CrisisFlow Dispatch Agent, an emergency medical supply coordination assistant.
Use only the JSON facts provided by the backend. Do not invent numbers, suppliers, approvals, routes, or statuses.
Separate prediction, recommendation, approval, and execution.
Never claim that life-critical actions have been executed unless the provided JSON says they were approved and dispatched.
Say "recommended" for proposed actions and "requires approval" for high-risk actions.
Keep the writing concise, operational, and auditable.
"""


def briefing_prompt(audience: str, payload: dict[str, Any]) -> str:
    return (
        f"{SYSTEM_GUARDRAILS}\n\n"
        f"Generate a {audience} briefing for the following CrisisFlow incident and dispatch data.\n"
        "Return plain markdown with a short title and 4-6 concise bullets.\n\n"
        f"DATA:\n{json.dumps(payload, indent=2, ensure_ascii=False, default=str)}"
    )


def explanation_prompt(payload: dict[str, Any]) -> str:
    return (
        f"{SYSTEM_GUARDRAILS}\n\n"
        "Generate concise operational explanations for each dispatch recommendation. "
        "Return JSON with recommendation action_id, why, risk_if_delayed, and data_used.\n\n"
        f"DATA:\n{json.dumps(payload, indent=2, ensure_ascii=False, default=str)}"
    )
