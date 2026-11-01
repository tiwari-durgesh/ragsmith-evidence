"""Synthetic engineering checks; not calibration or a selected evaluation set."""

import math

import pytest

from app.contracts import AskRequest
from app.evaluation_runner import prepare, run_case
from app.runtime import conservative_token_count
from tests.test_demo_api import request


class StubAnswerer:
    """Explicit test candidates with fabricated scores, never model confidence."""
    def __init__(self, change=None):
        self.change, self.calls = change, 0
    def count(self, prompt):
        return conservative_token_count(prompt)
    def generate(self, request, packed):
        self.calls += 1
        candidates = []
        for r in request.requirements:
            refs = [e.evidence_id for e in packed.evidence if r.metric in e.content]
            candidates.append({'requirement_id': r.requirement_id,
                               'value': '10' if r.metric == 'Revenue' else '4',
                               'citations': refs[:1], 'confidence': .8 if r.metric == 'Revenue' else .2})
        if self.change:
            self.change(candidates)
        return candidates, {'mode': 'synthetic stub; no model executed', 'inference_requests': 0}


def test_retrieval_shared_once_default_threshold_unset():
    answerer = StubAnswerer()
    result = run_case(AskRequest.model_validate(request()), answerer)
    assert answerer.calls == 1 and result['retrieval']['retrieved_units'] == 2
    assert result['packing']['input_tokens'] <= 3200
    assert result['policies'][0]['decision'] == 'full'
    assert result['policies'][2]['decision'] == 'full'
    confidence = result['policies'][1]
    assert confidence['decision'] is None and confidence['status'] == 'not_run_uncalibrated'
    assert result['confidence_threshold'] is None and result['confidence_calibrated'] is False
    assert result['research_ready'] is False


def test_explicit_synthetic_threshold_uses_same_generated_candidates():
    answerer = StubAnswerer()
    result = run_case(AskRequest.model_validate(request()), answerer, threshold=.5)
    never, confidence, graded = result['policies']
    assert answerer.calls == 1
    assert len(never['values']) == 2 and len(graded['values']) == 2
    assert [v['metric'] for v in confidence['values']] == ['Revenue']
    assert confidence['status'] == 'synthetic_threshold_only'
    assert not result['confidence_calibrated']


def test_conflicting_source_preserves_frozen_whole_question_abstention():
    payload = request([['Metric', '2025'], ['Revenue', '10'], ['Revenue', '20'], ['Cash', '4']])
    result = run_case(AskRequest.model_validate(payload), StubAnswerer())
    never, _, graded = result['policies']
    assert never['values'] and not never['citations_verified']
    assert graded['decision'] == 'abstain' and graded['values'] == [] and graded['citations'] == []


def test_wrong_cited_cell_does_not_become_verified_support():
    def wrong(candidates):
        candidates[0]['citations'] = candidates[1]['citations']
    result = run_case(AskRequest.model_validate(request()), StubAnswerer(wrong))
    graded = result['policies'][2]
    assert graded['decision'] == 'partial'
    assert [v['metric'] for v in graded['values']] == ['Cash']


@pytest.mark.parametrize('change', [
    lambda c: c.pop(),
    lambda c: c.reverse(),
    lambda c: c[0].update(confidence=math.nan),
    lambda c: c[0].update(citations=['invented']),
    lambda c: c[0].update(generation_failure=True),
])
def test_malformed_generation_stays_in_denominator_without_repair(change):
    answerer = StubAnswerer(change)
    result = run_case(AskRequest.model_validate(request()), answerer)
    assert result['status'] == 'generation_failed' and result['included_in_denominator']
    assert result['policies'] == [] and answerer.calls == 1


def test_empty_candidate_is_generation_failure_not_correct_abstention():
    result = run_case(AskRequest.model_validate(request()), StubAnswerer(lambda c: c[0].update(value='', citations=[])))
    assert result['status'] == 'generation_failed'
    assert result['generation_failures'] == ['r']
    assert result['included_in_denominator']


@pytest.mark.parametrize('threshold', [math.nan, math.inf, -1, 1.1, True])
def test_invalid_threshold_rejected_before_generation(threshold):
    answerer = StubAnswerer()
    with pytest.raises(ValueError, match='Threshold'):
        run_case(AskRequest.model_validate(request()), answerer, threshold=threshold)
    assert answerer.calls == 0


def test_tokenizer_noninteger_count_is_not_trusted():
    answerer = StubAnswerer()
    answerer.count = lambda _: 10.5
    with pytest.raises(ValueError, match='nonnegative integer'):
        prepare(AskRequest.model_validate(request()), answerer)
