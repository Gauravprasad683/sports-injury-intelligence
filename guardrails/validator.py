"""
Clinical Decision-Support Guardrails Validator
Implements programmatic verification for telemetry inputs, prompt injection detection,
clinical scope boundaries, and structured LLM outputs.
"""

import re
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field, field_validator


class PlayerTelemetryInput(BaseModel):
    """Pydantic model enforcing valid data ranges on player telemetry."""
    player_id: str = Field(..., description="Unique alphanumeric identifier (e.g. PLY-001)")
    name: str = Field(..., min_length=2, max_length=60)
    position: str = Field(..., description="Goalkeeper, Defender, Midfielder, Forward")
    acwr: float = Field(..., ge=0.1, le=4.0, description="Acute:Chronic Workload Ratio")
    avg_sleep_hours: float = Field(..., ge=2.0, le=14.0, description="Average sleep hours per night")
    wellness_score: float = Field(..., ge=1.0, le=10.0, description="Composite wellness rating")
    fatigue: float = Field(..., ge=1.0, le=10.0)
    soreness: float = Field(..., ge=1.0, le=10.0)
    stress: float = Field(..., ge=1.0, le=10.0)
    mood: float = Field(..., ge=1.0, le=10.0)
    acute_load_au: float = Field(default=1500.0, ge=100.0, le=6000.0)
    chronic_load_au: float = Field(default=1500.0, ge=100.0, le=6000.0)
    high_speed_running_m: float = Field(default=450.0, ge=0.0, le=5000.0)
    previous_injuries_count: int = Field(default=0, ge=0, le=20)

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: str) -> str:
        valid_positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
        if v not in valid_positions:
            # normalize if possible
            for pos in valid_positions:
                if pos.lower() in v.lower():
                    return pos
            raise ValueError(f"Position must be one of {valid_positions}, got '{v}'")
        return v

    @field_validator("player_id")
    @classmethod
    def sanitize_id(cls, v: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9\-_]", "", v)
        if not cleaned:
            raise ValueError("Invalid player_id format")
        return cleaned


class ClinicalBriefingOutput(BaseModel):
    """Pydantic model enforcing structured clinical briefing from LLM."""
    player_id: str
    player_name: str
    ml_risk_class: str
    risk_probability: float
    recommended_status: str
    protocol_rationale: str
    pitch_restrictions: str = "Standard progression"
    gym_restrictions: str = "Maintenance load"
    recovery_modalities: str = "Routine stretching and hydration"
    one_sentence_directive: str


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"bypass\s+(protocol|guardrail|security|rules)",
    r"reveal\s+(api\s+key|credentials|secret|system\s+prompt)",
    r"<script.*?>.*?</script>",
    r"javascript:",
    r"drop\s+table",
    r"exec\s*\(",
    r"system:\s*you\s+are",
]


def check_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Checks free-form text input against known prompt injection and attack patterns.
    Returns (is_safe: bool, reason: str).
    """
    if not text:
        return True, "Empty text"
    
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, f"Potential injection pattern detected matching rule: {pattern}"
    
    return True, "Safe"


def sanitize_text(text: str) -> str:
    """Removes HTML tags and unsafe characters from text."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", "", text)
    # Strip dangerous characters
    clean = re.sub(r"[\r\t]", " ", clean)
    return clean.strip()


def validate_player_payload(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validates a raw player dictionary against telemetry guardrails.
    Returns (is_valid, validated_dict, errors).
    """
    errors = []
    # Check injection in text fields
    for field in ["name", "notes", "last_injury_type"]:
        val = data.get(field, "")
        if isinstance(val, str):
            safe, reason = check_prompt_injection(val)
            if not safe:
                errors.append(f"Field '{field}' failed injection check: {reason}")

    try:
        validated = PlayerTelemetryInput(**data)
        return len(errors) == 0, validated.model_dump(), errors
    except Exception as e:
        errors.append(str(e))
        return False, data, errors


def verify_clinical_scope(text: str) -> Tuple[bool, List[str]]:
    """
    Scans generated clinical briefings to ensure the LLM has not made definitive
    medical diagnostic claims (e.g. 'Grade 3 ACL tear confirmed') or prescribed
    unauthorized medications.
    """
    violations = []
    text_lower = text.lower()
    
    prohibited_diagnostics = [
        "grade 3 tear confirmed",
        "i diagnose",
        "official diagnosis",
        "torn ligament confirmed",
        "broken bone",
        "fracture confirmed",
    ]
    
    prohibited_prescriptions = [
        "prescribe tramadol",
        "prescribe steroid",
        "corticosteroid injection mandated",
        "surgery required immediately",
    ]
    
    for phrase in prohibited_diagnostics:
        if phrase in text_lower:
            violations.append(f"AI diagnostic overreach: Detected '{phrase}'. Telemetry only supports risk probability, not definitive imaging diagnoses.")
            
    for phrase in prohibited_prescriptions:
        if phrase in text_lower:
            violations.append(f"Unauthorized pharmacological prescription: Detected '{phrase}'. Only load management and non-pharmacological recovery are permitted.")
            
    return len(violations) == 0, violations

