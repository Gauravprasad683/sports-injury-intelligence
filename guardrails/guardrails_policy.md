# CLINICAL DECISION-SUPPORT GUARDRAILS FRAMEWORK (CDS-GF)
**Document Version:** 2.4.0  
**Compliance Standard:** ISO/IEC 42001 (AI Management) & Sports Medicine Decision Safety  
**Enforcement Engine:** Multi-Tiered Algorithmic & LLM Operational Safeguards  

---

## 1. Executive Summary & Purpose

The **Clinical Decision-Support Guardrails Framework** establishes non-negotiable safety boundaries for the Elite Athletics Injury Risk Intelligence System. In elite sports medicine, automated predictive tools must never operate with autonomous clinical authority. The guardrails defined herein ensure strict data integrity, prevent adversarial manipulation or prompt injection, prohibit unauthorized diagnostic overreach, eliminate AI hallucinations, and guarantee continuous deterministic availability.

---

## 2. Guardrail Architecture & Layered Defense

```
[ Incoming Telemetry / User Input ]
             │
             ▼
┌──────────────────────────────────────────────┐
│ Layer 1: Input Validation & Sanitization     │
│ - Range & Type Checks (ACWR, Sleep, Wellness)│
│ - Adversarial & Prompt Injection Defense     │
└──────────────────────────────────────────────┘
             │ (Clean / Validated)
             ▼
┌──────────────────────────────────────────────┐
│ Layer 2: Machine Learning Prediction Bounds  │
│ - Probability Calibration [0.00, 1.00]       │
│ - Feature Vector Anomaly Detection           │
└──────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Layer 3: Protocol-Grounded LLM RAG Bounds    │
│ - System Prompt Inoculation                  │
│ - Strict Grounding against medical-protocol  │
│ - Output Schema Conformity (briefing-template)│
└──────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Layer 4: Output Post-Validation & Safety     │
│ - Medical Scope Enforcement (No Diagnosis)   │
│ - Hallucination Verification                 │
│ - Fallback Rule Execution on 429/Failure     │
└──────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Layer 5: Human Medical Checkpoint Gate       │
│ - Mandatory Licensed Staff Sign-Off          │
│ - Immutable Audit Trail & Override Logging   │
└──────────────────────────────────────────────┘
             │
             ▼
[ Rendered Decision / Cleared Action ]
```

---

## 3. Tier 1: Input Validation & Integrity Guardrails

All player telemetry data (whether loaded from `player_health_data.json` or entered interactively via the "Add Player" module) must pass strict boundary validation:

| Telemetry Parameter | Allowed Range / Type | Clinical Rationale / Edge Handling |
| :--- | :--- | :--- |
| `Player ID` | String matching `PLY-[0-9]{3,4}` | Uniform identification, prevents code injection. |
| `Player Name` | Alphabetic + spaces, 2–50 chars | Sanitized against script tags, HTML, SQL tokens. |
| `Position` | Enum (`Goalkeeper`, `Defender`, `Midfielder`, `Forward`) | Standard tactical designations. |
| `ACWR` | Float `[0.10, 3.50]` | Physiological extremes beyond 3.5 indicate sensor malfunction; clamped & flagged. |
| `Avg Sleep Hours` | Float `[2.0, 14.0]` | Realistic human restorative limits. |
| `Wellness Score` | Float `[1.0, 10.0]` | Standard Likert/Hooper-Mackinnon composite. |
| `Fatigue / Soreness` | Float `[1.0, 10.0]` | Sub-scores must correlate with composite wellness. |
| `Acute Load (AU)` | Float `[100.0, 5000.0]` | Arbitrary units of sRPE or GPS meter volume. |
| `Chronic Load (AU)`| Float `[200.0, 4500.0]` | Rolling 4-week base load. |
| `HSR Distance (m)` | Float `[0.0, 3500.0]` | Meters run > 21 km/h per session. |

### Prompt Injection Defense
Free-form text fields (e.g. physiotherapist notes, player names, custom telemetry labels) are filtered against known injection patterns:
- Direct system override triggers: `ignore previous instructions`, `bypass protocol`, `reveal api key`, `system prompt`.
- Markdown/HTML exploit tags: `<script>`, `javascript:`, `<iframe>`, `data:`.

---

## 4. Tier 2: Clinical Scope & Diagnostic Limitation Guardrails

The LLM RAG engine is explicitly prohibited from generating definitive diagnostic assertions or prescribing medical treatments beyond load management:

1. **No Autonomous Diagnoses:**
   - **Prohibited:** "Player has a Grade 2 Biceps Femoris tear."
   - **Permitted / Enforced:** "Elevated acute spike in HSR (+32%) indicates heightened statistical risk of hamstring strain. Prescribe ultrasound screening."
2. **Mandatory Disclaimer Injection:**
   - Every briefing and output card must carry the clinical decision support disclaimer:
     > *"Decision Support Simulation Only. All medical clearances require signed review by the Club Doctor or Lead Physiotherapist."*
3. **No Pharmacological Prescriptions:**
   - System prompts forbid recommending prescription NSAIDs, corticosteroid injections, or surgical interventions. Only physical therapy modalities, cryotherapy, and load tapering are within scope.

---

## 5. Tier 3: Grounding & Hallucination Suppression Guardrails

To prevent LLM confabulation:
1. **Fresh Ingestion Requirement:** The primary protocol document `medical-protocol.md` and formatting document `briefing-template.md` are read fresh from disk on every evaluation cycle.
2. **Explicit Citation Requirement:** The generated briefing must cite the specific threshold from `medical-protocol.md` (e.g., "Clause 1: ACWR > 1.50 Critical Zone", "Clause 2: Sleep < 6.0 Hours Severe Deprivation").
3. **Pydantic Schema Validation:** The LLM output is parsed against a Pydantic data model. If JSON output fails parsing or lacks required sections, the engine retries or fails over immediately to the deterministic rule engine.

---

## 6. Tier 4: Rate Limiting & Deterministic Fallback Engine

When operating on Groq's high-speed API:
1. **Free-Tier Protection & Exponential Backoff:**
   - If HTTP 429 (Too Many Requests) or HTTP 503 is encountered, the client pauses and retries with exponential backoff: `2s -> 4s -> 8s`.
2. **Dual-Model Cascade:**
   - Primary: `llama-3.3-70b-versatile` (deep clinical reasoning).
   - Backup: `llama-3.1-8b-instant` (lightweight, rapid failover).
3. **Deterministic Protocol Fallback Engine:**
   - If Groq API credentials are unavailable, network fails, or all retries are exhausted, the system seamlessly triggers the **Internal Deterministic Rule Engine**.
   - The rule engine evaluates the exact mathematical boundaries from `medical-protocol.md` and generates a compliant briefing, tagging the result as `Decided By: Fallback Rule`.
   - The application **never crashes** due to API outages.

---

## 7. Tier 5: Human Medical Checkpoint Gate

The ultimate safeguard is human agency:
- **No Automatic Roster Locking:** The AI cannot unilaterally bar a player from competition without clinical sign-off.
- **Explicit Override Channel:** Club doctors can override AI risk classifications from `High Risk` to `Cleared` (or vice versa), provided a clinical justification note is recorded in the immutable audit log.
- **Audit Logging:** Every status change, override, and physio note is stamped with the user identity and timestamp in `st.session_state`.

