# ASCRIBE: Atomic and Significance-Based Reasoning for Thai Clinical SOAP Note Generation

[![arXiv](https://img.shields.io/badge/arXiv-2610.01234-b31b1b.svg)](https://arxiv.org/abs/2610.01234)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-loolootech-ffc107)](https://huggingface.co/loolootech)

Tarm Kalavantavanich, Teerawut Ponarchar, Pattaramanee Arsomngern, Jenta Wonglertsakul, Watcharakorn Chuthong, Chiraphat Boonnag, Knot Pipatsrisawat, Titipat Achakulvisut<br>

> Accepted to WiNLP @ EMNLP 2026.

## Overview

ASCRIBE is a physician-inspired reasoning framework for writing SOAP notes from Thai doctor–patient conversations. Before writing the note, the model extracts atomic facts from the transcript, grounds each fact in a short supporting span, and assigns it one of six clinical-significance levels. It then generates the SOAP note in the same pass, conditioned on this reasoning trace.

The paper applies ASCRIBE in two ways:

- **As a prompt.** ASCRIBE outperforms chain-of-thought prompting on GPT-5.4 and Gemini 3.1 Pro across the physician-aligned LLM-judge metrics, and improves on standard prompting by up to 10.3 points on the completeness metric.
- **As GRPO rewards.** Rewarding atomic-fact extraction, significance labels, completeness, and factual grounding enables a Gemma-4-E4B model trained only on synthetic data to match Gemini 3.1 Pro in factual precision and surpass it in completeness.

The paper also releases two Thai datasets: S-ICOPD, a synthetic training corpus, and ThaiClinicBench, a benchmark of real clinical encounters.

## Datasets

The datasets can be found on Hugging Face. Both are released under a controlled-access, research-only data license (see App. H of the paper).

| Dataset | Description | Link |
|---|---|---|
| S-ICOPD | Synthetic Thai doctor–patient transcripts seeded from physician-written SOAP notes, with model-generated reference atomic facts and SOAP notes. Used for training. | [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-S--ICOPD-ffc107)](https://huggingface.co/datasets/loolootech/S-ICOPD) |
| ThaiClinicBench | 44 de-identified real outpatient encounters from a Thai clinic, each pairing a transcript with a physician-written SOAP note. Used as an out-of-distribution test set. | [![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-ThaiClinicBench-ffc107)](https://huggingface.co/datasets/loolootech/ThaiClinicBench) |

The ICOPD corpus used in the main experiments is private and is not released.


## Prompts

The prompt figures in the paper show only the instructions. The files in [`prompts/`](prompts/) hold the complete prompts, including the input templates and the worked examples omitted from the figures.

| Prompt | Paper | File |
|---|---|---|
| Standard SOAP note generation | App. A.1, Fig. 4 | [`default_prompt.py`](prompts/default_prompt.py) |
| Chain-of-thought SOAP note generation | App. A.2, Fig. 5 | [`cot_prompt.py`](prompts/cot_prompt.py) |
| ASCRIBE structured reasoning | App. A.3, Fig. 6 | [`ascribe_prompt.py`](prompts/ascribe_prompt.py) |
| Reference SOAP note refinement | App. A.4, Fig. 7 | [`refinement_prompt.py`](prompts/refinement_prompt.py) |
| Atomic fact extraction | App. B.1, Fig. 8 | [`atomic_extract_prompt.py`](prompts/atomic_extract_prompt.py) |
| ReferenceRecall judge | App. B.1, Fig. 9 | [`atomic_judge_recall_prompt.py`](prompts/atomic_judge_recall_prompt.py) |
| GeneratedPrecision judge | App. B.1, Fig. 10 | [`atomic_judge_precision_prompt.py`](prompts/atomic_judge_precision_prompt.py) |
| Clinical significance classification | App. B.2, Fig. 11 | [`sig_classify_prompt.py`](prompts/sig_classify_prompt.py) |
| ClaimEntailment judge | App. D.1, Fig. 13 | [`ce_prompt.py`](prompts/ce_prompt.py) |
| SOAPPrecision judge | App. D.2, Fig. 14 | [`sp_prompt.py`](prompts/sp_prompt.py) |

Each prompt file is self-contained and depends only on the Python standard library (Python 3.9+). It defines:

- `SYSTEM_PROMPT` — the system instruction.
- `USER_TEMPLATE` — the input template, with `{placeholders}` for the inputs.
- `build_user_prompt(...)` — fills `USER_TEMPLATE` from raw inputs.

To print every user prompt built from mock inputs:

```bash
python prompts/example.py
```


## License

The code and prompts in this repository are released under the [MIT License](LICENSE). The ClaimEntailment ([`ce_prompt.py`](prompts/ce_prompt.py)), SOAPPrecision ([`sp_prompt.py`](prompts/sp_prompt.py)) and reference SOAP note refinement ([`refinement_prompt.py`](prompts/refinement_prompt.py)) prompts are adapted from [DocLens](https://github.com/yiqingxyq/DocLens), also released under the MIT License; its notice is kept in each of those files.

The S-ICOPD and ThaiClinicBench datasets are not covered by this license. They are released on Hugging Face under a controlled-access, research-only data license (see App. H of the paper).


## Citation

```bibtex
@misc{kalavantavanich2026ascribe,
  title         = {ASCRIBE: Atomic and Significance-Based Reasoning for Thai Clinical SOAP Note Generation},
  author        = {Tarm Kalavantavanich and Teerawut Ponarchar and Pattaramanee Arsomngern and Jenta Wonglertsakul and Watcharakorn Chuthong and Chiraphat Boonnag and Knot Pipatsrisawat and Titipat Achakulvisut},
  year          = {2026},
  eprint        = {2610.01234},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/2610.01234}
}
```
