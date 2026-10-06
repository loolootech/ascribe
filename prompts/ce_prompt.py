# The prompt in this file is adapted from DocLens
# (https://github.com/yiqingxyq/DocLens), used under the MIT License:
#
# MIT License
#
# Copyright (c) 2024 Yiqing Xie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json

SYSTEM_PROMPT = """Please act as an impartial judge and evaluate whether the Thai clinical note provided by an AI assistant can fully entail each claim below.
Also generate an explanation for your answer. For each claim, please output 1 or 0 for each claim, where 1 means the claim
can be fully entailed by the clinical note, and 0 means the claim contains information that cannot be entailed by the clinical note.

Use strict textual/logical entailment. Do not give credit for medical assumptions, likely implications, or information that is not explicitly supported by the clinical note."""

USER_TEMPLATE = """Input:
{{
  "clinical note": "PHYSICAL EXAM\\n- Cardiovascular: 3/6 systolic ejection murmur, previously noted.\\n- Extremities: 1+ pitting edema in lower extremities.",
  "claims": [
    {{"claim_id": 0, "claim": "The patient's blood pressure is high."}},
    {{"claim_id": 1, "claim": "The patient has a grade 3/6 systolic ejection murmur."}},
    {{"claim_id": 2, "claim": "The patient exhibits 1+ pitting edema in both lower extremities."}}
  ]
}}

Example output:
{{
  "evaluations": [
    {{
      "claim_id": 0,
      "claim": "The patient's blood pressure is high.",
      "explanation": "The clinical note does not mention the blood pressure.",
      "entailment_prediction": 0
    }},
    {{
      "claim_id": 1,
      "claim": "The patient has a grade 3/6 systolic ejection murmur.",
      "explanation": "The PHYSICAL EXAM section explicitly states a 3/6 systolic ejection murmur.",
      "entailment_prediction": 1
    }},
    {{
      "claim_id": 2,
      "claim": "The patient exhibits 1+ pitting edema in both lower extremities.",
      "explanation": "The note states 1+ pitting edema in lower extremities but does not establish both sides.",
      "entailment_prediction": 0
    }}
  ]
}}

Now evaluate this input:
{{
  "clinical note": {clinical_note_json},
  "claims": {claims_json}
}}

Return structured JSON with one evaluation for every claim. Preserve each claim_id and the original claim text."""


SOAP_SECTION_NAMES = {
    "history_of_present_illness": "HISTORY OF PRESENT ILLNESS",
    "physical_exam": "PHYSICAL EXAM",
    "results": "RESULTS",
    "assessment_and_plan": "ASSESSMENT AND PLAN",
}


def build_user_prompt(soap_note: dict[str, list[str]], claims: list[str]) -> str:
    """Fill `USER_TEMPLATE` with the note rendered as text and the claims, indexed from 0.

    `soap_note` is the generated SOAP note, `claims` are the reference atomic facts.
    """
    clinical_note = "\n\n".join(
        f"{section_name}\n" + ("\n".join(f"- {point}" for point in soap_note.get(field, [])) or "-")
        for field, section_name in SOAP_SECTION_NAMES.items()
    )
    return USER_TEMPLATE.format(
        clinical_note_json=json.dumps(clinical_note, ensure_ascii=False),
        claims_json=json.dumps(
            [{"claim_id": idx, "claim": claim} for idx, claim in enumerate(claims)],
            ensure_ascii=False,
            indent=2,
        ),
    )
