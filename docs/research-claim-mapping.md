# Research claims and falsification plan

Source: the user-confirmed proposal DOCX, particularly Research Question,
Objectives, Evidence-Sufficiency Layer, Evidence-Bounded Generation, Citation
Generation, Experimental Design, and Novelty. This is an operationalization of
those claims, not evidence that they are already true. Production policy and
the original research question remain unchanged.

## Direct hypothesis and controlled comparisons

Primary claim: with identical evidence and extraction, graded requirement-level
sufficiency returns more correct supported information for partial questions
than binary abstention, while avoiding the unsupported claims of extraction
without verification. Retrieval gains must not be credited to sufficiency.

The pilot explicitly supplies requirements. It tests the sufficiency mechanism
on controlled fact sets, not automatic natural-language decomposition. A finance
extraction subset cannot establish all-domain, heterogeneous reasoning ability.

| Baseline or comparison | Proposal claim tested | What stays fixed | Status |
| --- | --- | --- | --- |
| Extraction only vs graded sufficiency | Evidence-bounded generation reduces unsupported complete-looking answers; relevance alone is insufficient. | Requirements, evidence union, extracted candidates/order and available provenance. Only decision/verification policy changes. | Implemented for synthetic fixtures. |
| Binary sufficiency vs graded sufficiency | Three-way sufficiency preserves useful supported information instead of discarding partial answers. | Same extraction and verifier judgments; binary responds only when all requirements are supported. | Implemented for synthetic fixtures. |
| Controlled full/partial/absent/conflict evidence sets | Sufficiency depends on which required facts are present, not merely topic similarity. | Same base facts, question requirements and family; only a documented evidence condition changes. | Synthetic fixtures implemented; source-derived conditions pending annotation. |
| Frozen retrieved evidence vs oracle source-linked evidence | Separate retrieval failure from sufficiency failure. | Same question/scope, requirements, verifier and response mechanism. | Tracks A/B implemented with synthetic frozen rankings; real retrieval experiment pending. |
| Dense; BM25+dense; BM25+dense+table; KG; full heterogeneous hybrid | The proposed retrieval combination improves evidence coverage and supports text/table/relationship questions. | Fixed question set, comparable candidate budget, generator and sufficiency policy. | Original proposal comparisons preserved; unimplemented and untested. |
| Full hybrid with and without sufficiency | Integrated sufficiency improves reliability over the same hybrid RAG pipeline. | Exact retrieved set and generator, prompt and evidence budget. | Required for the full proposal; the small deterministic pilot does not substitute for it. |

Extraction-only is deliberately a weak diagnostic control, not a state-of-the-art
RAG baseline. It reports a nonempty answer as its binary answer decision and
cannot predict partial; interpret its three-class score in that context. Binary
vs graded is the tighter test of the added third decision class. A shared
classifier's judgments do not independently establish their factual correctness;
source-based gold annotations do that.

Binary abstention has zero partial-response coverage by construction. Showing
that graded output beats it on a deliberately constructed perfect partial case
is a software check, not a surprising research finding. The real test is whether
independent source annotations confirm sufficient facts in imperfect retrieved
contexts without raising false-support risk. Current canonical-row equality
checking is a narrow consistency mechanism, not demonstrated semantic entailment
or general evidence sufficiency. Report this limitation rather than claiming
the synthetic comparison proves the proposed contribution.

## Every proposed metric mapped to a claim

| Metric | Specific proposal claim and interpretation | Implemented now? |
| --- | --- | --- |
| Recall@k, MRR, nDCG; support/conflict recall | Hybrid retrieval recovers decisive evidence, including facts whose omission can make an answer misleading. Evaluate retrieval separately from sufficiency. | Yes for synthetic frozen ranking logs; full hybrid comparisons remain pending. |
| Three-class accuracy, confusion matrix, macro-F1 | Evidence-Sufficiency Layer distinguishes complete, partial and insufficient/conflicted cases. | Yes, synthetic Track A. |
| Supported requirement coverage, micro and macro | Objectives call for retaining information that can be supported, rather than unnecessarily discarding it. | Yes. |
| Partial-answer completeness | Evidence-Bounded Generation should answer supported portions of partial questions. Primary comparison: graded vs binary. | Yes. |
| Unsupported-claim rate | Prevent unsupported generation; primary comparison: graded vs extraction-only. A definitive disputed value counts as unsupported under the fixed conservative policy. | Yes, restricted atomic-fact rubric. |
| Citation precision, uncited-claim count | Citation Generation should point to evidence supporting the particular returned fact, not merely a relevant passage. Gold links plus correct value and matching provenance are required. | Yes for annotated fixture links; independent source annotations needed for real data. |
| Abstention precision | Abstention should be appropriate to genuinely insufficient or conflicted scoped evidence. | Yes. |
| Over-abstention | Objective explicitly seeks reliability without unnecessarily discarding supportable information. | Yes. |
| Answer EM/token-F1 | Answer Quality assesses returned content, but lexical similarity cannot establish correctness or support. Secondary only. | No. |
| Faithfulness | Claims must have source support. In the atomic extraction pilot the operational measure is supported/unsupported claim accounting, not a general LLM judge score. | Restricted rubric only. |
| Answer relevance | Responses should address requested facts. Initial rubric aligns emitted claim IDs/metric/year to requirements; broader semantic relevance is not established. | Field alignment enforced; no general relevance score. |
| Coverage-risk analysis | Quantify the tradeoff between retaining useful answers and avoiding unsafe claims, across policy choices. | Counts and paired source-cluster intervals for primary differences implemented; plots and real data pending. |
| Confidence calibration | Proposal lists calibrated confidence evaluation. No confidence variable currently exists; metadata completeness is not one. | Deferred until a confidence model is explicitly defined. |
| Stage latency and peak memory | Practicality of a local-first system on modest hardware is a constraint, not the central novelty claim. | Diagnostic harness timing and optional Python allocation peak implemented; live retrieval latency and process RSS remain unmeasured. |

Null denominators remain null. Unsupported formats whose sources are human-
answerable remain failures in overall scoring; do not recategorize them as
gold missing. Corpus labels and retrieved-set labels are separate estimands.

## Results that would refute or limit the claims

**Originality:** a prior verified work predating our contribution that already
implements and evaluates the same requirement-level graded mechanism over the
claimed heterogeneous evidence and source-bounded responses would refute a
claim that this integration is original. That is a literature finding, not a
benchmark score. The literature review is still incomplete. Individual components
are established and are not claimed as new.

**Empirical benefit:** predeclare two primary paired endpoints before held-out
scoring: supported coverage on gold partial questions (graded minus binary),
and unsupported-claim rate (graded minus extraction-only), with per-policy
coverage also shown. A precise nonpositive coverage effect and no reliability
advantage over extraction-only contradict the pilot benefit hypothesis. A
reliability gain achieved solely by suppressing all answers does not satisfy
the joint claim. Material increases in unsupported claims versus binary without
the promised coverage benefit would also contradict it.

**Proposed practical margin for review:** a 1 percentage-point maximum increase
in unsupported-claim rate versus binary is a candidate non-inferiority margin,
not an approved threshold or a result this pilot is powered to certify. Freeze
any margin with the user after calibration and before held-out scoring; do not
choose it after seeing model outcomes. If a paired interval is wholly above an
agreed risk margin, the safety claim fails at that tolerance. If intervals are
wide or cross zero/margins, the result is inconclusive, not proof or falsification.

**Heterogeneous integration:** if controlled full-system ablations later show
no useful coverage or reliability contribution from adding table/KG evidence,
or the sufficiency mechanism systematically fails on those formats, the claimed
heterogeneous advantage is unsupported or contradicted. A table-only pilot cannot
verify it either way.

**Robustness:** gains that vanish under independent review, group-preserving
splits, removal of label leakage, or equal evidence budgets invalidate the
purported result. Gold labels derived from the tested verifier cannot establish
its accuracy. Native dataset scores and our derived stress-task scores must
never be presented as interchangeable leaderboard results.

This pilot can falsify narrow operational claims or expose design failures. A
positive result cannot prove novelty, general enterprise superiority, or the
complete research architecture's benefit.
