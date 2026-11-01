"""Corpus runner acceptance checks with invented sources and an injected stub."""

import json

import pytest

from app.research.corpus_runner import Excerpt, StudyRequest, GenerationCache, build_corpus, run_batch
from app.runtime import conservative_token_count


class Stub:
    def __init__(self, fail=False):
        self.calls, self.fail = 0, fail
    def count(self, prompt):
        return conservative_token_count(prompt)
    def generate(self, request, packed):
        self.calls += 1
        if self.fail:
            raise RuntimeError('Do not log this private prompt')
        return [{'requirement_id': r.requirement_id, 'value': '10' if r.metric=='Revenue' else '4',
                 'confidence': .8, 'citations': [e.evidence_id for e in packed.evidence if r.metric in e.content][:1]}
                for r in request.requirements], {'mode':'synthetic stub', 'inference_requests':0}


def excerpt(uid='one', group='g', value='10'):
    return Excerpt(context_id=uid,group_id=group,table=[['Metric','2025'],['Revenue',value]])


def question(case='q', scope=None):
    return StudyRequest(case_id=case,question='Give Revenue in 2025.', group_id='g',context_ids=scope or ['one'],
                        requested_facts=[{'requirement_id':'r','metric':'Revenue','year':2025}])


def test_corpus_retrieves_fixed_scope_excluding_distractor_and_reuses_cache(tmp_path):
    corpus=build_corpus([excerpt(),excerpt('distractor','other','900')],tmp_path/'corpus')
    cache=GenerationCache(tmp_path/'cache',{'model':'synthetic-v1'})
    stub=Stub()
    a=run_batch(corpus,[question()],stub,cache)
    b=run_batch(corpus,[question()],stub,cache)
    assert stub.calls==1 and a['results_sha256']==b['results_sha256']
    assert b['execution']['generation_cache_hits']==1
    result=b['results'][0]
    assert result['retrieval']['retrieved_units']==1
    assert result['packing']['input_tokens']<=3200
    assert result['policies'][2]['decision']=='full'
    assert result['policies'][1]['decision'] is None
    assert result['confidence_threshold'] is None


def test_shared_two_source_conflict_uses_same_candidates_and_frozen_rule(tmp_path):
    corpus=build_corpus([excerpt(),excerpt('two',value='20')],tmp_path/'corpus')
    stub=Stub()
    result=run_batch(corpus,[question(scope=['one','two'])],stub,GenerationCache(tmp_path/'cache',{'model':'stub'}))['results'][0]
    assert stub.calls==1
    assert result['policies'][0]['values']
    assert result['policies'][2]['decision']=='abstain'
    assert not result['policies'][2]['citations']


def test_generation_failure_is_cached_without_retry_or_private_log(tmp_path,caplog):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    cache=GenerationCache(tmp_path/'cache',{'model':'stub'})
    stub=Stub(fail=True)
    a=run_batch(corpus,[question()],stub,cache)
    b=run_batch(corpus,[question()],stub,cache)
    assert stub.calls==1 and a['results_sha256']==b['results_sha256']
    assert b['results'][0]['status']=='generation_failed'
    assert b['results'][0]['included_in_denominator']
    assert 'private prompt' not in caplog.text


def test_preparation_failure_keeps_request_in_denominator(tmp_path):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    stub=Stub()
    report=run_batch(corpus,[question(scope=['unknown'])],stub,GenerationCache(tmp_path/'cache',{'model':'stub'}))
    assert report['requested_cases']==1 and stub.calls==0
    assert report['results'][0]['status']=='preparation_failed'
    assert report['results'][0]['included_in_denominator']


def test_mutated_source_or_database_fails_closed(tmp_path):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    Path=type(tmp_path)
    Path(corpus.contexts['one']['source_path']).write_text('tamper',encoding='utf-8')
    result=run_batch(corpus,[question()],Stub(),GenerationCache(tmp_path/'cache',{'model':'stub'}))['results'][0]
    assert result['status']=='preparation_failed'


def test_corrupt_or_interrupted_cache_does_not_generate_again(tmp_path):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    cache=GenerationCache(tmp_path/'cache',{'model':'stub'})
    stub=Stub()
    run_batch(corpus,[question()],stub,cache)
    record=next((tmp_path/'cache').glob('*.json'))
    data=json.loads(record.read_text(encoding='utf-8'))
    data['record']['candidates'][0]['value']='999'
    record.write_text(json.dumps(data),encoding='utf-8')
    result=run_batch(corpus,[question()],stub,cache)['results'][0]
    assert result['status']=='generation_failed' and stub.calls==1
    record.unlink()  # Disposable synthetic test fixture only; claim remains.
    assert run_batch(corpus,[question()],stub,cache)['results'][0]['status']=='generation_failed'
    assert stub.calls==1


def test_stable_corpus_and_case_order_independent_of_input_order(tmp_path):
    contexts=[excerpt(),excerpt('two','other')]
    a=build_corpus(contexts,tmp_path/'a')
    b=build_corpus(list(reversed(contexts)),tmp_path/'b')
    cache=GenerationCache(tmp_path/'cache',{'model':'stub'})
    x=run_batch(a,[question('b'),question('a')],Stub(),cache)
    y=run_batch(b,[question('a'),question('b')],Stub(),cache)
    assert a.sha256==b.sha256
    assert x['results_sha256']==y['results_sha256']
    assert [r['question_id'] for r in y['results']]==['a','b']


def test_changed_runtime_identity_cannot_reuse_generation(tmp_path):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    stub=Stub()
    for name in ('stub-v1','stub-v2'):
        run_batch(corpus,[question()],stub,GenerationCache(tmp_path/'cache',{'model':name}))
    assert stub.calls==2


def test_duplicate_cases_rejected_before_generation(tmp_path):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    with pytest.raises(ValueError,match='Duplicate'):
        run_batch(corpus,[question(),question()],Stub(),GenerationCache(tmp_path/'cache',{'model':'stub'}))


def test_registered_fallback_runs_without_changing_other_policies(tmp_path):
    corpus=build_corpus([excerpt()],tmp_path/'corpus')
    result=run_batch(corpus,[question()],Stub(),GenerationCache(tmp_path/'cache',{'model':'stub'}),threshold='always_abstain')['results'][0]
    assert result['policies'][0]['decision']=='full'
    assert result['policies'][1]['decision']=='abstain'
    assert result['policies'][2]['decision']=='full'
