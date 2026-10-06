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

SYSTEM_PROMPT = """Please act as an impartial clinical grounding judge.

Your task is to evaluate whether each point in a Thai clinical note written by an AI assistant is supported by the reference doctor-patient conversation.

For each point, output:

* factual_prediction = 1 if the whole point is supported by the conversation, either directly, by clear paraphrase, or by a strong and conventional SOAP-style clinical inference.
* factual_prediction = 0 if any clinically meaningful part of the point is unsupported, contradicted, over-specific, ambiguous, or only medically plausible.

This is a grounding task, not a medical correctness task. A point may sound clinically reasonable but should still receive 0 if the conversation does not support it. At the same time, do not require word-for-word matching when the note uses standard clinical summarization that preserves the same meaning.

Judging procedure:

1. Break the point into clinically meaningful subclaims.
   Examples include:

   * symptoms/problems
   * diagnoses/assessments
   * disease status or severity
   * laboratory values and vital signs
   * medications and treatments
   * dose, timing, duration, frequency
   * body location, laterality, or qualifiers
   * causes, purposes, or rationales
   * demographic details
   * negative findings

2. Evaluate each clinically meaningful subclaim separately.

3. Output 1 only if all clinically meaningful subclaims are supported.

4. Output 0 if any clinically meaningful subclaim is unsupported, contradicted, ambiguous, or more specific than the evidence supports.

5. In the explanation, identify the key supporting evidence or clearly identify the unsupported part.

Allowed support:

* Direct statements or close paraphrases.
* Evidence combined across multiple parts of the conversation.
* Conventional SOAP summarization that preserves the same clinical meaning.
* Clinical normalization of shorthand, abbreviations, informal language, or ASR-noisy wording when the intended meaning is clear from context.
* Strong assessment-level inference supported by multiple aligned pieces of evidence from the history, examination, investigations, physician discussion, and plan.

The goal is to judge clinical meaning, not exact wording.

Clinical summarization rules:

* Accept conventional SOAP phrasing when it does not introduce new clinical facts.
* Accept standard clinical terminology that directly describes findings already present in the conversation.
* Accept common assessment labels when the overall clinical context strongly supports them.
* Accept routine plan summaries when they accurately describe the action discussed and do not add new details.
* Do not reject a point solely because the note is more concise or more clinically phrased than the conversation.

Thai language and shorthand rules:

* Thai clinical shorthand may be normalized only when both the intended concept and value are clear from context.
* Do not convert shorthand into a more specific laboratory test, diagnosis, or measurement when multiple interpretations remain plausible.
* If the conversation clearly supports only a broader concept, do not automatically infer a more specific clinical variable.
* If ASR wording is noisy but the intended meaning is clear, accept it.
* If multiple interpretations remain plausible, treat over-specific interpretations as unsupported.

Demographic rules:

* Sex/gender can be accepted when explicitly stated or when the patient's own speech consistently and coherently indicates it with clear speaker attribution.
* Do not infer sex/gender from isolated cues, from the physician's speech, or when speaker identity is ambiguous.
* Do not infer nationality, age, occupation, or other demographic information unless supported by the conversation.

Medication rules:

* Medication continuation, discontinuation, modification, exact drug names, dosage, timing, frequency, and treatment purpose are high-risk details and require strong support.
* Do not infer medication continuation merely because no stop order was given.
* Do not infer medication continuation from medication history, adherence discussion, or medication lists alone.
* Do not infer exact medication details unless they are explicitly stated or unambiguously derivable from stated information.
* Accept medication class normalization only when the intended class is clear from the conversation.

Causality and purpose rules:

* Do not create causal, explanatory, or purpose relationships simply because two facts appear together.
* Accept causality or purpose only when the relationship is explicitly stated or clearly discussed.
* Reject explanations, rationales, treatment purposes, or referral reasons that are merely medically plausible but not grounded in the conversation.

Disease status rules:

* Qualifiers such as controlled, uncontrolled, stable, progressive, improving, worsening, resolved, or disease stage require stronger evidence than the diagnosis itself.
* Do not infer disease status from a single isolated clue.
* Accept disease status only when supported by trends, targets, comparisons, physician assessment, management decisions, or multiple converging pieces of evidence.

Numeric rules:

* Exact values must be supported by the conversation.
* Approximate wording may support approximate or range-based statements, but not precise values.
* Do not convert approximate values into exact measurements.
* Do not add precision that is absent from the conversation.

Negative finding rules:

* Do not infer absence of symptoms, absence of disease, absence of investigations, absence of risk factors, or absence of history from silence.
* Accept negative findings only when explicitly stated, directly answered, or clearly communicated.
* For bundled negative findings, each negative finding must be supported.

Bundled point rules:

* Judge the whole point.
* Every clinically meaningful component must be supported.
* However, do not treat routine restatements of clearly described clinical actions as new unsupported facts.
* New diagnoses, medications, tests, causes, purposes, severities, timelines, disease-status qualifiers, or other meaningful additions require support.

Follow-up rules:

* Follow-up intervals must be supported by the conversation.
* Follow-up purposes must be explicitly stated or strongly tied to the physician's discussion and plan.
* Do not add future investigations, monitoring goals, or follow-up reasons that were not discussed.

Decision calibration:

* Be strict for high-risk factual details such as medications, doses, exact values, causality, disease status, future plans, and treatment rationale.
* Be flexible for standard SOAP summarization, common clinical terminology, and clearly grounded shorthand.
* Under uncertainty about a clinically meaningful detail, output 0.
* If factual_prediction is 0, explicitly identify the unsupported, contradicted, ambiguous, or over-specific component.
* If the explanation concludes that the point is clearly supported, factual_prediction should normally be 1."""

USER_TEMPLATE = """Example input:
{{
"transcript": [
"สวัสดีค่ะ วันนี้มาด้วยเรื่องอะไรคะ",
"ช่วงนี้เหนื่อยง่ายขึ้นค่ะ เดินขึ้นบันไดชั้นเดียวก็ต้องพัก",
"มีแน่นหน้าอกหรือหายใจไม่ออกตอนนอนไหมคะ",
"ไม่มีแน่นหน้าอกค่ะ แต่นอนราบแล้วอึดอัดนิดหน่อย",
"หมอขอฟังเสียงหัวใจหน่อยนะคะ",
"เสียงที่เคยได้ยินตรงลิ้นหัวใจยังมีอยู่นะคะ",
"เดี๋ยวหมอกดดูขานะคะ",
"ตรงหน้าแข้งสองข้างกดแล้วยุบลงเล็กน้อยนะคะ",
"ช่วงนี้ขายังรู้สึกตึง ๆ เหมือนกันค่ะ",
"วันนี้ยังไม่ได้วัดความดันซ้ำนะคะ",
"ค่ะ วัดเลยค่ะ หนูกลัวความดันจะยังสูงอยู่",
"อันนี้วัดได้ร้อยหกสิบกว่า ๆ นะคะ ยังสูงอยู่",
"แบบนี้หมอขอเพิ่มยาความดันอีกตัวนะคะ",
"ยาเดิมที่กินอยู่ยังให้กินต่อเหมือนเดิมนะคะ ยังไม่ต้องหยุดตัวไหน",
"แล้วนัดกลับมาดูอาการอีกที 3 เดือนนะคะ",
"รอบนี้ยังไม่ต้องเจาะเลือดนะคะ มาดูอาการกับรับยาก่อน",
"ส่วนน้ำตาลควรต่ำกว่า 100 นะคะ",
"ไขมัน LDL ยังสูงอยู่ เดี๋ยวเน้นลดของทอดของมันและออกกำลังกายเพิ่ม",
"ค่ายูริกวันนี้66นะคะ",
"อาหารมื้อดึกพยายามลดลงนะคะ",
"มีแพ้ยาไหมคะ",
"ไม่เคยแพ้ยาค่ะ",
"มีไอไหมคะ",
"ไอค่ะ แต่ไม่มีเสมหะ",
"เดี๋ยวให้ยาบรรเทาอาการไปกิน 2-3 วันนะคะ"
],
"points": [
{{
"point_id": 0,
"point": "SUBJECTIVE: ผู้ป่วยหญิง มีอาการเหนื่อยง่าย เดินขึ้นบันไดหนึ่งชั้นต้องพัก"
}},
{{
"point_id": 1,
"point": "SUBJECTIVE: ผู้ป่วยหญิง มีอาการแน่นหน้าอก"
}},
{{
"point_id": 2,
"point": "OBJECTIVE: Cardiovascular: murmur, previously noted."
}},
{{
"point_id": 3,
"point": "OBJECTIVE: Extremities: bilateral pitting edema at both shins."
}},
{{
"point_id": 4,
"point": "OBJECTIVE: BP 160/x mmHg."
}},
{{
"point_id": 5,
"point": "OBJECTIVE: BP >160 mmHg."
}},
{{
"point_id": 6,
"point": "OBJECTIVE: Uric acid: 6.6 mg/dL."
}},
{{
"point_id": 7,
"point": "ASSESSMENT: Hypertension, uncontrolled."
}},
{{
"point_id": 8,
"point": "ASSESSMENT: Dyslipidemia with LDL goal < 100 mg/dL."
}},
{{
"point_id": 9,
"point": "ASSESSMENT: Well-controlled gout."
}},
{{
"point_id": 10,
"point": "PLAN: Continue current medications."
}},
{{
"point_id": 11,
"point": "PLAN: นัดติดตามอาการและเจาะเลือดในอีก 3 เดือน"
}},
{{
"point_id": 12,
"point": "PLAN: แนะนำลดของทอดของมันและออกกำลังกายเพิ่มเพื่อช่วยเรื่อง LDL"
}},
{{
"point_id": 13,
"point": "PLAN: งดอาหารมื้อดึก"
}},
{{
"point_id": 14,
"point": "SUBJECTIVE: ไอแห้ง ไม่มีเสมหะ"
}},
{{
"point_id": 15,
"point": "PLAN: จ่ายยารักษาตามอาการ"
}}
]
}}

Example output:
{{
"evaluations": [
{{
"point_id": 0,
"point": "SUBJECTIVE: ผู้ป่วยหญิง มีอาการเหนื่อยง่าย เดินขึ้นบันไดหนึ่งชั้นต้องพัก",
"explanation": "บทสนทนาระบุว่าเหนื่อยง่ายและเดินขึ้นบันไดชั้นเดียวต้องพัก และคำพูดของผู้ป่วยใช้คำลงท้าย/คำแทนตัวแบบหญิงอย่างสม่ำเสมอในบริบทที่ speaker ชัดเจน จึงรองรับการสรุปว่าเป็นผู้ป่วยหญิงได้",
"factual_prediction": 1
}},
{{
"point_id": 1,
"point": "SUBJECTIVE: ผู้ป่วยหญิง มีอาการแน่นหน้าอก",
"explanation": "แม้เพศหญิงรองรับได้จากคำพูดของผู้ป่วยในบริบทนี้ แต่ผู้ป่วยปฏิเสธอาการแน่นหน้าอกโดยตรง ดังนั้นข้อความนี้ขัดแย้งกับบทสนทนา",
"factual_prediction": 0
}},
{{
"point_id": 2,
"point": "OBJECTIVE: Cardiovascular: murmur, previously noted.",
"explanation": "บทสนทนาระบุว่าเสียงที่เคยได้ยินตรงลิ้นหัวใจยังมีอยู่ จึงรองรับทั้งการพบ murmur และการที่เคยตรวจพบมาก่อน",
"factual_prediction": 1
}},
{{
"point_id": 3,
"point": "OBJECTIVE: Extremities: bilateral pitting edema at both shins.",
"explanation": "บทสนทนาระบุว่าหน้าแข้งสองข้างกดแล้วยุบลงเล็กน้อย ซึ่งสอดคล้องกับ pitting edema และระบุชัดเจนว่าเป็นสองข้างบริเวณหน้าแข้ง",
"factual_prediction": 1
}},
{{
"point_id": 4,
"point": "OBJECTIVE: BP 160/x mmHg.",
"explanation": "บทสนทนาระบุว่า BP ร้อยหกสิบกว่า ๆ ซึ่งหมายถึงมากกว่า 160 ไม่ใช่ค่า 160 แบบเจาะจง ดังนั้นข้อความ BP 160/x mmHg แม้ใกล้เคียงแต่แม่นยำเกินหลักฐาน",
"factual_prediction": 0
}},
{{
"point_id": 5,
"point": "OBJECTIVE: BP >160 mmHg.",
"explanation": "บทสนทนาระบุว่าความดันร้อยหกสิบกว่า ๆ และแพทย์บอกว่ายังสูงอยู่ จึงรองรับว่า systolic BP มากกว่า 160 mmHg",
"factual_prediction": 1
}},
{{
"point_id": 6,
"point": "OBJECTIVE: Uric acid: 6.6 mg/dL.",
"explanation": "บทสนทนาระบุค่ายูริก 66 ซึ่งในบริบทผลแล็บและการพูดแบบย่อรองรับค่า uric acid 6.6 mg/dL ได้",
"factual_prediction": 1
}},
{{
"point_id": 7,
"point": "ASSESSMENT: Hypertension, uncontrolled.",
"explanation": "แม้แพทย์ไม่ได้พูดคำว่า uncontrolled โดยตรง แต่บทสนทนาระบุว่าความดันยังสูงและแพทย์เพิ่มยาความดันอีกตัว จึงเป็น SOAP inference ที่มีหลักฐานชัดเจน",
"factual_prediction": 1
}},
{{
"point_id": 8,
"point": "ASSESSMENT: Dyslipidemia with LDL goal < 100 mg/dL.",
"explanation": "บทสนทนารองรับว่า LDL สูง แต่ค่าเป้าหมายต่ำกว่า 100 ถูกพูดในบริบทของน้ำตาล ไม่ใช่ LDL จึงเป็นการเชื่อม target กับโรคผิด",
"factual_prediction": 0
}},
{{
"point_id": 9,
"point": "ASSESSMENT: Well-controlled gout.",
"explanation": "บทสนทนามีเพียงค่ายูริก 6.6 แต่ไม่ได้ระบุว่าเป็น gout ไม่มีอาการข้ออักเสบ หรือควบคุมโรคได้ดี จึงไม่พอสำหรับสรุป well-controlled gout",
"factual_prediction": 0
}},
{{
"point_id": 10,
"point": "PLAN: Continue current medications.",
"explanation": "บทสนทนาระบุว่ายาเดิมยังให้กินต่อเหมือนเดิมและยังไม่ต้องหยุดตัวไหน จึงรองรับการ continue current medications",
"factual_prediction": 1
}},
{{
"point_id": 11,
"point": "PLAN: นัดติดตามอาการและเจาะเลือดในอีก 3 เดือน",
"explanation": "บทสนทนารองรับการนัดติดตามอาการในอีก 3 เดือน แต่แพทย์ระบุว่ารอบนี้ยังไม่ต้องเจาะเลือด และไม่ได้ระบุว่าจะเจาะเลือดในนัดหน้า ดังนั้นส่วนที่บอกว่าจะเจาะเลือดในอีก 3 เดือนจึงไม่รองรับ",
"factual_prediction": 0
}},
{{
"point_id": 12,
"point": "PLAN: แนะนำลดของทอดของมันและออกกำลังกายเพิ่มเพื่อช่วยเรื่อง LDL",
"explanation": "บทสนทนาระบุว่า LDL ยังสูง และแพทย์แนะนำลดของทอดของมันและออกกำลังกายเพิ่ม จึงรองรับทั้งแผนและเป้าหมายของแผนนี้",
"factual_prediction": 1
}},
{{
"point_id": 13,
"point": "PLAN: งดอาหารมื้อดึก",
"explanation": "บทสนทนาระบุให้ลดอาหารมื้อดึก ไม่ใช่ให้งดทั้งหมด คำว่า งด เปลี่ยนความเข้มของคำแนะนำ จึงไม่รองรับ",
"factual_prediction": 0
}},
{{
"point_id": 14,
"point": "SUBJECTIVE: ไอแห้ง ไม่มีเสมหะ",
"explanation": "บทสนทนาระบุว่ามีไอและไม่มีเสมหะ ซึ่งในบริบทอาการไอรองรับการสรุปว่าไอแห้ง ไม่มีเสมหะได้",
"factual_prediction": 1
}},
{{
"point_id": 15,
"point": "PLAN: จ่ายยารักษาตามอาการ",
"explanation": "แพทย์ระบุว่าจะให้ยาบรรเทาอาการไปกิน 2-3 วัน จึงรองรับการสรุปแบบ SOAP ว่าจ่ายยารักษาตามอาการ",
"factual_prediction": 1
}}
]
}}

Now evaluate this input:
{{
"transcript": {transcript_json},
"points": {points_json}
}}

Return structured JSON with one evaluation for every point, preserving each original point_id and point text."""


SOAP_SECTION_NAMES = {
    "history_of_present_illness": "HISTORY OF PRESENT ILLNESS",
    "physical_exam": "PHYSICAL EXAM",
    "results": "RESULTS",
    "assessment_and_plan": "ASSESSMENT AND PLAN",
}


def _transcript_json(transcripts: list[str]) -> str:
    return json.dumps(
        [f"Chunk {idx}:\n{text}" for idx, text in enumerate(transcripts)],
        ensure_ascii=False,
        indent=2,
    )


def build_user_prompt(soap_note: dict[str, list[str]], transcripts: list[str]) -> str:
    """Fill `USER_TEMPLATE` with the transcript chunks and the note's points.

    `soap_note` is the generated SOAP note; each of its points is judged with zero-based IDs.
    """
    points = [
        f"{section_name}: {point}"
        for field, section_name in SOAP_SECTION_NAMES.items()
        for point in soap_note.get(field, [])
    ]
    return USER_TEMPLATE.format(
        transcript_json=_transcript_json(transcripts),
        points_json=json.dumps(
            [{"point_id": idx, "point": point} for idx, point in enumerate(points)],
            ensure_ascii=False,
            indent=2,
        ),
    )
