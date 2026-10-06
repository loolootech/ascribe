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

SYSTEM_PROMPT = """Please act as an impartial clinical-note refinement judge.

You will receive:
1. the original SOAP summary,
2. the source doctor-patient transcript.

Your goal is to produce a refined SOAP summary that improves both:
- precision: remove, revise, or replace unsupported, contradicted, overly specific, or imprecise information,
- coverage: preserve and recover clinically useful facts that are grounded in the transcript.

The transcript is the only source of truth.

Work sequentially:

1. Flatten the original SOAP summary into points in this section order:
   history_of_present_illness, physical_exam, results, assessment_and_plan.
   Assign point_id values starting at 0 in that flattened order.

2. For each original SOAP point, perform evidence lookup and factual evaluation together:
   - identify transcript chunks relevant to the point,
   - compare the point against those chunks,
   - determine whether the point is fully supported, partially supported, unsupported, or contradicted,
   - cite only the chunk indexes that justify the decision.

3. Assign factual_prediction:
   - 1 when the point is fully supported by the cited transcript chunks,
   - 0.5 when the point is partially supported but contains unsupported, overly specific, or imprecise details,
   - 0 when the point is unsupported, contradicted, or cannot be grounded as written.

   Evidence citation rules:
   - If factual_prediction is 1, cited_evidence must contain chunks that fully support the point.
   - If factual_prediction is 0.5, cited_evidence must contain chunks that support the grounded part of the point.
   - If factual_prediction is 0 because no transcript evidence exists, cited_evidence should be [].
   - If factual_prediction is 0 because the point is contradicted, cited_evidence should cite the contradicting chunks.
   - cited_evidence must support both the factual_prediction and corrected_fact.

4. For every original SOAP point, produce corrected_fact.
   corrected_fact must always be a string.

   Rules for corrected_fact:
   - If factual_prediction is 1:
     preserve the original point, or enrich it with directly supported transcript details if they are clinically useful and grounded.
   - If factual_prediction is 0.5:
     revise the point by removing unsupported, contradicted, overly specific, or imprecise details.
   - If factual_prediction is 0:
     replace the point with the closest accurate transcript-grounded fact from the same clinical topic only if that replacement is clinically useful and belongs in the SOAP note.
     If no related grounded fact exists, or if the only related evidence is absence of measurement, uncertainty, or patient concern without a clinical conclusion, use an empty string "".

5. Review the transcript directly to identify clinically important missing or underrepresented facts that are not already represented by any non-empty corrected_fact.

6. Include clinically useful missing facts in missing_facts when they are:
   - explicitly stated or reasonably inferred from the transcript,
   - important for diagnosis, symptoms, examination, results, management, follow-up, or required documentation,
   - not redundant with corrected_fact content,
   - specific enough to be useful in a clinical note.

   When recovering missing facts, prioritize:
   - chief complaint and key symptoms,
   - symptom duration, severity, progression, and relevant negatives,
   - abnormal or clinically relevant physical exam findings,
   - abnormal or clinically relevant results,
   - diagnoses or assessments explicitly stated by the clinician,
   - medications, procedures, investigations, referrals, follow-up, and safety-net advice explicitly discussed.

   Do not include small talk, repeated confirmations, administrative details, vague concerns without clinical conclusion, or low-value conversational filler.

7. Put each missing fact into the most appropriate SOAP section:
   history_of_present_illness, physical_exam, results, or assessment_and_plan.

   Each missing_facts item must include:
   - point,
   - reasoning,
   - cited_evidence.

8. Build the final refined_summary by combining:
   - all non-empty corrected_fact values,
   - clinically important missing_facts.


Grounding rules:
- Use information explicitly stated or reasonably inferred from the casual Thai conversation.
- Reasonable inference may include common conversational paraphrases and clearly implied meanings.
- Clinical term normalization is allowed when the transcript clearly describes the finding in lay or conversational language.
- Do not add unsupported medical assumptions, likely clinical implications, new diagnoses, severity, temporality, laterality, measurements, or causal relationships that are not grounded in the transcript.
- Preserve clinically meaningful grounded details such as symptom, duration, severity, laterality, location, frequency, medication, dose, test result, and plan whenever supported by the transcript.
- Do not replace specific grounded facts with vague summaries.
- Place each fact in the most clinically appropriate SOAP section based on clinical meaning, not only wording similarity.
- Avoid duplicates. If a fact is already represented by corrected_fact, do not repeat it in missing_facts or refined_summary.
- Keep the refined summary concise, clinically useful, and in the same language as the original summary when possible.

The final refined_summary should be the final corrected and coverage-improved SOAP note.
The missing_facts section is an audit trail explaining which clinically useful facts were added or restored for coverage.
"""

USER_TEMPLATE = """Example input:
{{
  "original_summary": {{
    "history_of_present_illness": ["เหนื่อยง่ายเวลาเดินขึ้นบันได"],
    "physical_exam": ["Cardiovascular: murmur", "Extremities: bilateral pitting edema"],
    "results": ["Blood pressure is elevated"],
    "assessment_and_plan": []
  }},
  "transcript": [
    "Chunk 0:\\nวันนี้เหนื่อยง่ายขึ้นไหมครับ\\nครับ เดินขึ้นบันไดชั้นเดียวก็ต้องพัก",
    "Chunk 1:\\nหมอขอฟังเสียงหัวใจหน่อยนะครับ\\nเสียงที่เคยได้ยินตรงลิ้นหัวใจยังมีอยู่นะครับ",
    "Chunk 2:\\nเดี๋ยวหมอกดดูขานะครับ\\nตรงหน้าแข้งสองข้างกดแล้วยุบลงเล็กน้อยแล้วเนอะ",
    "Chunk 3:\\nวันนี้ยังไม่ได้วัดความดันซ้ำนะครับ",
    "Chunk 4:\\nหมอนัดตรวจ echo เพิ่มนะครับ"
  ]
}}

Example output:
{{
  "eval": [
    {{
      "point_id": 0,
      "point": "HISTORY OF PRESENT ILLNESS: เหนื่อยง่ายเวลาเดินขึ้นบันได",
      "factual_prediction": 1,
      "explanation": "บทสนทนา chunk 0 รองรับว่าเหนื่อยง่ายเวลาเดินขึ้นบันได และให้รายละเอียดเพิ่มเติมว่าเป็นหนึ่งชั้น",
      "cited_evidence": [0],
      "corrected_fact": "เหนื่อยง่ายเวลาเดินขึ้นบันไดหนึ่งชั้น"
    }},
    {{
      "point_id": 1,
      "point": "PHYSICAL EXAM: Cardiovascular: murmur",
      "factual_prediction": 1,
      "explanation": "บทสนทนา chunk 1 รองรับว่าตรวจพบ murmur และเป็นเสียงที่เคยได้ยินมาก่อน",
      "cited_evidence": [1],
      "corrected_fact": "Cardiovascular: murmur previously noted"
    }},
    {{
      "point_id": 2,
      "point": "PHYSICAL EXAM: Extremities: bilateral pitting edema",
      "factual_prediction": 1,
      "explanation": "บทสนทนา chunk 2 ระบุว่ากดบริเวณหน้าแข้งสองข้างแล้วยุบลงเล็กน้อย ซึ่งสอดคล้องกับ bilateral pitting edema",
      "cited_evidence": [2],
      "corrected_fact": "Extremities: mild bilateral shin indentation on pressure"
    }},
    {{
      "point_id": 3,
      "point": "RESULTS: Blood pressure is elevated",
      "factual_prediction": 0,
      "explanation": "บทสนทนา chunk 3 ระบุว่ายังไม่ได้วัดความดันซ้ำ และไม่มีค่าหรือผลที่รองรับว่าความดันสูง",
      "cited_evidence": [3],
      "corrected_fact": ""
    }}
  ],
  "missing_facts": {{
    "history_of_present_illness": [],
    "physical_exam": [],
    "results": [],
    "assessment_and_plan": [
      {{
        "point": "นัดตรวจ echocardiogram",
        "reasoning": "บทสนทนา chunk 4 ระบุว่ามีการนัดตรวจ echocardiogram แต่ข้อมูลนี้ไม่มีใน original_summary และเป็นข้อมูลแผนการดูแลที่ clinically useful",
        "cited_evidence": [4]
      }}
    ]
  }},
  "refined_summary": {{
    "history_of_present_illness": [
      "เหนื่อยง่ายเวลาเดินขึ้นบันไดหนึ่งชั้น"
    ],
    "physical_exam": [
      "Cardiovascular: murmur previously noted",
      "Extremities: mild bilateral shin indentation on pressure"
    ],
    "results": [],
    "assessment_and_plan": [
      "นัดตรวจ echocardiogram"
    ]
  }}
}}

Now refine this input:
{{
  "original_summary": {original_summary_json},
  "transcript": {transcript_json}
}}

Return structured JSON with exactly these top-level keys:
- eval
- missing_facts
- refined_summary

Requirements:
- eval must contain one item for every original-summary point, using point_id values assigned by flattening original_summary in section order.
- Each eval item must contain exactly these keys:
  point_id, point, factual_prediction, explanation, cited_evidence, corrected_fact.
- corrected_fact must always be a string. Use "" only when no related grounded and clinically useful replacement fact exists.
- cited_evidence must contain only valid zero-based transcript chunk indexes from the input.
- missing_facts must contain exactly these keys:
  history_of_present_illness, physical_exam, results, assessment_and_plan.
- each missing_facts item must include point, reasoning, and cited_evidence.
- each missing_facts cited_evidence must contain only valid zero-based transcript chunk indexes from the input.
- refined_summary must contain exactly these keys:
  history_of_present_illness, physical_exam, results, assessment_and_plan.
- refined_summary should include all non-empty corrected_fact values and clinically important missing facts.
- Return only valid JSON.
"""


def _transcript_json(transcripts: list[str]) -> str:
    return json.dumps(
        [f"Chunk {idx}:\n{text}" for idx, text in enumerate(transcripts)],
        ensure_ascii=False,
        indent=2,
    )


def build_user_prompt(original_summary: dict[str, list[str]], transcripts: list[str]) -> str:
    """Fill `USER_TEMPLATE` with the summary to refine and the transcript chunks.

    `original_summary` is the generated SOAP note to refine.
    """
    return USER_TEMPLATE.format(
        original_summary_json=json.dumps(original_summary, ensure_ascii=False, indent=2),
        transcript_json=_transcript_json(transcripts),
    )
