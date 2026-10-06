SYSTEM_PROMPT = """Summarize the Thai doctor-patient conversation to generate a Thai clinical note with four sections: HISTORY OF PRESENT
ILLNESS, PHYSICAL EXAM, RESULTS, ASSESSMENT AND PLAN.

Solve it in a step-by-step fashion, return your answer in the following
format, PROVIDE DETAILED ANALYSIS BEFORE THE RESULT:

Return valid JSON that matches this schema exactly:
{{
  "reasoning_steps": "free-form analysis of how the conversation maps to each SOAP section",
  "history_of_present_illness": ["point 1", "point 2"],
  "physical_exam": ["point 1"],
  "results": ["point 1"],
  "assessment_and_plan": ["point 1"]
}}

Use concise Thai clinical wording in the final SOAP sections, keeping common medical terms in English when appropriate. Use [] for sections not present in the conversation. Do not invent details. The conversation is:"""

USER_TEMPLATE = "{transcript}"


def build_user_prompt(transcripts: list[str]) -> str:
    """Join the transcript utterances, skipping empty ones."""
    return USER_TEMPLATE.format(transcript="\n".join(u for u in transcripts if u))
