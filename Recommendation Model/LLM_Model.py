"""
Gemini LLM-powered detailed recommendation service.

Takes crop type, disease, rule-based remedies, and farm size as inputs,
then generates a structured advisory covering:
  1. Why the disease occurs (root cause analysis)
  2. Cure details with specific products
  3. Application timing and method
  4. Cost analysis based on farm size
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Models to try in order — if the primary model's quota is exhausted, fall back
_GEMINI_MODELS: list[str] = [
    os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
]

_MAX_RETRIES = 3
_BASE_DELAY = 2.0  # seconds


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


_SYSTEM_PROMPT = """\
You are an expert agricultural scientist and plant pathologist. \
You provide detailed, evidence-based, actionable advisories for farmers.

IMPORTANT: Respond ONLY with a valid JSON object (no markdown, no code fences, no extra text). \
The JSON must have exactly these keys:

{
  "cause_analysis": "string — 3-5 sentences explaining WHY this disease occurs (environmental factors, pathogen biology, favourable conditions)",
  "cure_details": [
    {
      "product_name": "string — commercial / generic name",
      "type": "string — Fungicide | Insecticide | Bio-agent | Nutrient | Cultural Practice",
      "active_ingredient": "string",
      "dosage_per_acre": "string — amount per acre with units"
    }
  ],
  "application_guide": [
    {
      "stage": "string — crop growth stage",
      "timing": "string — when to apply",
      "method": "string — how to apply (foliar spray, seed treatment, soil drench, etc.)",
      "precautions": "string — safety/weather precautions"
    }
  ],
  "cost_analysis": {
    "farm_size_acres": <number>,
    "items": [
      {
        "product_name": "string",
        "quantity_required": "string — total amount for the given farm size",
        "unit_price_inr": "string — approximate market price per unit",
        "total_cost_inr": "string — quantity × unit price"
      }
    ],
    "labour_cost_inr": "string — estimated labour/spraying cost",
    "total_estimated_cost_inr": "string — grand total"
  }
}

All prices should be in Indian Rupees (₹ / INR). \
Use current approximate Indian market prices for pesticides, fungicides, and nutrients. \
Be realistic and practical. Do not invent unrealistic prices.
"""


def _build_user_prompt(
    crop: str,
    disease: str,
    remedies: list[str],
    farm_size_acres: float,
) -> str:
    remedies_text = "\n".join(f"  - {r}" for r in remedies) if remedies else "  (none provided)"
    return (
        f"Crop: {crop}\n"
        f"Detected Disease: {disease}\n"
        f"Rule-Based Remedies already suggested:\n{remedies_text}\n"
        f"Farm Size: {farm_size_acres} acres\n\n"
        f"Based on the above, generate the full JSON advisory."
    )


def _extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from the LLM response, tolerating markdown fences."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)


async def generate_detailed_recommendation(
    crop: str,
    disease: str,
    remedies: list[str],
    farm_size_acres: float,
) -> dict[str, Any]:
    """Call Gemini to produce a structured advisory JSON.

    Retries on rate-limit (429) errors and falls back to alternate models.
    """
    client = _get_client()
    user_prompt = _build_user_prompt(crop, disease, remedies, farm_size_acres)

    last_error: Exception | None = None

    for model_name in _GEMINI_MODELS:
        for attempt in range(_MAX_RETRIES):
            try:
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=_SYSTEM_PROMPT,
                        temperature=0.4,
                        max_output_tokens=8192,
                    ),
                )

                raw_text = response.text or ""

                try:
                    result = _extract_json(raw_text)
                except (json.JSONDecodeError, ValueError):
                    result = {"raw_response": raw_text, "parse_error": True}

                if "cost_analysis" in result and isinstance(result["cost_analysis"], dict):
                    result["cost_analysis"]["farm_size_acres"] = farm_size_acres

                return result

            except Exception as exc:
                last_error = exc
                err_str = str(exc)
                # Only retry on rate-limit / quota errors
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    # If it says "limit: 0" the daily quota is gone — skip to next model
                    if "limit: 0" in err_str:
                        break
                    # Otherwise wait and retry the same model
                    await asyncio.sleep(_BASE_DELAY * (2 ** attempt))
                    continue
                # Non-rate-limit error — raise immediately
                raise

    # All models exhausted
    raise RuntimeError(
        f"All Gemini models quota exhausted. Please try again later. Last error: {last_error}"
    )
