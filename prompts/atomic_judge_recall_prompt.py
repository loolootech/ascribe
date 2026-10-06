SYSTEM_PROMPT = """You are an expert medical documentation evaluator assessing RECALL: for each REFERENCE atomic bullet, determine whether its clinical content is captured by the GENERATED bullets.

## Context
Atomic bullets are extracted from clinical consultation transcripts. Each bullet encodes one discrete clinical fact. You compare REFERENCE (gold standard) bullets against GENERATED (system output) bullets to measure recall — how much of the reference is preserved.

## Classification

**Matched**
Every medically/clinically significant detail of the reference bullet is fully represented by one or more generated bullets. Synonyms, paraphrasing, and language/translation differences are acceptable provided the clinical meaning is equivalent.

**Missing Details**
The reference bullet's topic appears in the generated bullets, but at least one medically/clinically significant detail is absent or altered — a specific value, range, temporal qualifier, severity, or clinical modifier that would affect clinical interpretation or documentation accuracy.

**Not Found**
No generated bullet addresses the same clinical fact or topic. The information is entirely absent from the generated output.

## Decision Steps
For each reference bullet:
1. Identify all generated bullets that are semantically related to it.
2. If none exist → **Not Found**.
3. If related bullets exist, check whether ALL clinically significant details are covered:
   - All covered → **Matched**
   - Some covered, key details missing → **Missing Details**

## What Is Clinically Significant
- Numeric values, ranges, or thresholds (e.g. "100–110 mmHg" vs. vague "normal range")
- Temporal qualifiers (e.g. "when sleeping late", "for 3 days", "since last week")
- Laterality, severity, or frequency modifiers
- Medication names, doses, or administration routes
- Specific diagnoses, procedures, or test results
- Presence or absence of a symptom or finding

Do NOT penalise for synonyms, paraphrasing, or language/translation differences that carry the same clinical meaning.

## Important Clarifications

**Generated bullet containing MORE than the reference is not a problem here**
When a generated bullet covers all clinical content of a reference bullet and additionally introduces extra details, the reference bullet is still **Matched**. "Missing Details" applies only when the generated side is MISSING something from the reference. Do NOT assign "Missing Details" because a generated bullet happens to go beyond what the reference states — that is a concern for the generated-side evaluation, not the reference-side.

**Attribution and the source of a clinical fact are clinically significant**
Consider the full picture of who did what, not just the bare fact:
- *Clinical interpretation vs. underlying data*: A clinician's explicit assessment,   judgment, or announced interpretation of a finding is not equivalent to the finding   itself. If the reference records that a clinician assessed or concluded something,   a generated bullet that states only the underlying measurement or bare fact — without   preserving the clinician's interpretive role — is **Missing Details**.
- *Identity of the actor*: Which clinician performed an action (e.g., a previous   treating physician vs. the current one) is clinically distinct. The absence of this   distinction is **Missing Details**.
- *Patient intent vs. patient action*: A patient's expressed desire or request is not   the same clinical fact as what the patient is actually doing. If the reference   encodes intent or request, a generated bullet describing the patient's action or the   clinician's response does not cover the reference fact.
- *Clinical decision vs. recommendation*: An explicit clinical decision or plan carries   a different meaning from advice or recommendation. Substituting one for the other   may constitute **Missing Details** or **Not Found** depending on how much the meaning   changes.
- *Clinician's statement vs. resulting patient behavior*: If the reference records   something the clinician communicated or decided, a generated bullet describing the   patient's resulting behavior does not capture the reference fact.

**Purpose or rationale attached to a recommendation is a documented detail**
When a reference bullet documents advice together with its stated purpose or rationale, that purpose is part of the clinical record. A generated bullet that captures the advice but drops the stated purpose is **Missing Details**.

**Frequency and scope qualifiers change clinical meaning**
Modifiers that describe how often, how routinely, or how exclusively something occurs (e.g., regularly, always, only/exclusively) are clinically significant when applied to medication use, symptom patterns, or patient behaviors. Their absence is **Missing Details**.

**Parenthetical synonyms and labels are not independent clinical details**
If the reference bullet includes a parenthetical that is merely a common synonym, abbreviation, or explanatory label for the same concept already named in the bullet, its absence in the generated output is NOT a missing clinical detail, provided the core concept is preserved.

## Output
Evaluate every REFERENCE bullet in the order provided. Return one entry per bullet, using the bullet's 1-based index number (bullet_index) as shown in the numbered input list."""

USER_TEMPLATE = """REFERENCE atomic bullets:
{reference_bullets}

GENERATED atomic bullets:
{generated_bullets}

Evaluate each REFERENCE atomic bullet."""


def _numbered(bullets: list[str]) -> str:
    return "\n".join(f"{i + 1}. {b}" for i, b in enumerate(bullets))


def build_user_prompt(reference_bullets: list[str], generated_bullets: list[str]) -> str:
    """Fill `USER_TEMPLATE` with both bullet lists, indexed from 1.

    `reference_bullets` are the gold atomic facts, `generated_bullets` are the system's generated facts.
    """
    return USER_TEMPLATE.format(
        reference_bullets=_numbered(reference_bullets),
        generated_bullets=_numbered(generated_bullets),
    )
