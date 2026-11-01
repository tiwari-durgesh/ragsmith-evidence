"""Selection is executed only on invented candidates in these tests."""

from collections import Counter
from dataclasses import replace
import hashlib
from itertools import combinations
import json

import pytest

from app.research.selection import (CaseSpec, DEVELOPMENT,EVALUATION,NotFeasible,SearchNotCertified,
                                    priority,question_is_duplicate,reserve_joint,source_groups)
from scripts.tatqa_excerpt_ingestion import digest,excerpt_groups


def pool():
    mixes=[['full','full','partial','missing','conflict'],
           ['full','full','partial','partial','missing'],
           ['full','full','partial','missing','conflict'],
           ['full','full','partial','partial','conflict'],
           ['full','full','partial','partial','conflict'],
           ['full','full','partial','partial','conflict'],
           ['full','full','partial','missing','conflict'],
           ['full','full','partial','missing','conflict'],
           ['full','full','partial','partial','missing'],
           ['full','full','partial','missing','missing']]
    groups=[];cases=[]
    for i,mix in enumerate(mixes):
        uid=f'context-{i}';gid='excerpt-group-'+digest([uid])
        groups.append({'group_id':gid,'members':[uid],'excluded':False,'independence_established':False})
        for j,stratum in enumerate(mix):
            fact=f'fact-{i}-{j}'
            cases.append(CaseSpec(gid,(uid,),(fact,),f'Give synthetic metric {i}-{j}.',
                                  (('r',f'metric {i}-{j}',2025),),(fact,),stratum,True))
    return groups,cases


def draw(groups,cases,**kw):
    return reserve_joint(groups,cases,pilot_questions=(),source_pool_sha256=digest('synthetic-source'),**kw)


def test_priorities_match_registered_canonical_sha256():
    expected=hashlib.sha256(json.dumps([1729,'development','g'],separators=(',',':')).encode()).digest()
    assert priority('development','g')==(expected,'g')


def test_exact_joint_mix_cap_no_fact_reuse_and_deterministic_order():
    groups,cases=pool()
    a=draw(groups,cases);b=draw(list(reversed(groups)),list(reversed(cases)))
    assert a.sha256==b.sha256
    assert Counter(c.stratum for c in a.development)==DEVELOPMENT
    assert Counter(c.stratum for c in a._evaluation)==EVALUATION
    assert set(c.group_id for c in a.development).isdisjoint(c.group_id for c in a._evaluation)
    assert set(Counter(c.group_id for c in a.development+a._evaluation).values())=={5}
    assert len({f for c in a.development+a._evaluation for f in c.fact_ids})==50


def test_first_development_group_tuple_matches_independent_exhaustive_oracle():
    groups,cases=pool()
    ordered=sorted([g['group_id'] for g in groups],key=lambda g:priority('development',g))
    expected=next(combo for combo in combinations(ordered,4)
                  if Counter(c.stratum for c in cases if c.group_id in combo)==DEVELOPMENT)
    actual=draw(groups,cases)
    assert sorted({c.group_id for c in actual.development},key=lambda g:priority('development',g))==list(expected)


def test_evaluation_materialization_requires_matching_development_lock():
    r=draw(*pool())
    assert 'evaluation' not in r.development_packet()
    for lock in ({},{'locked':True,'threshold':None,'development_selection_sha256':r.development_sha256},
                 {'locked':True,'threshold':.5,'development_selection_sha256':'wrong'}):
        with pytest.raises(ValueError):r.materialize_evaluation(lock)
    assert len(r.materialize_evaluation({'locked':True,'threshold':.5,
                                       'development_selection_sha256':r.development_sha256}))==30


def test_infeasible_or_uncertified_pool_stops_instead_of_relaxing_mix():
    groups,cases=pool()
    with pytest.raises(NotFeasible):draw(groups,[c for c in cases if c.stratum!='conflict'])
    with pytest.raises(SearchNotCertified):draw(groups,cases,max_nodes=1)
    groups[0]['excluded']=True
    with pytest.raises(NotFeasible):draw(groups,cases)


def test_reused_underlying_fact_and_uncertified_source_cannot_fill_slots():
    groups,cases=pool()
    cases[0]=replace(cases[0],fact_ids=cases[1].fact_ids)
    with pytest.raises(NotFeasible):draw(groups,cases)
    groups,cases=pool();cases[0]=replace(cases[0],source_certified=False)
    with pytest.raises(NotFeasible):draw(groups,cases)


def test_pilot_question_exact_and_three_shingle_screens():
    assert question_is_duplicate(' Revenue in 2025? ',('revenue in 2025?',))
    assert not question_is_duplicate('Cash?',('Revenue?',))


def test_source_family_name_hash_and_transitive_quarantine():
    families={f'family-{i}' for i in range(8)}
    pilot={'context_id':'pilot','table':[['A','2025'],['B','1'],['C','2']], 'paragraphs':[]}
    contexts=[{'context_id':'copy','table':pilot['table'],'paragraphs':[]},
              {'context_id':'family','table':[['D','2024'],['E','3']], 'report_family':'family-0'},
              {'context_id':'name','table':[['F','2023'],['G','4']], 'paragraphs':['American Tower Corporation']},
              {'context_id':'linked','table':[['H','2022'],['I','5']], 'near_duplicate_links':['name']},
              {'context_id':'clear','table':[['J','2021'],['K','6']]}]
    groups,ledger=source_groups(contexts,[pilot],family_ids=families,excluded_context_ids=set())
    excluded={row['context_id'] for row in ledger}
    assert {'pilot','copy','family','name','linked'}<=excluded and 'clear' not in excluded
    assert any(row['rules']==['transitive_quarantine'] for row in ledger if row['context_id']=='linked')


def test_precomputed_groups_match_existing_pairwise_screens():
    contexts=[{'context_id':str(i),'table':[[f'Label {i}','2025'],['Cash',str(i)],['Other',str(i+10)]]} for i in range(8)]
    contexts[2]['table']=contexts[1]['table']
    actual,_=source_groups(contexts,[],family_ids={str(i) for i in range(8)},excluded_context_ids=set())
    expected=excerpt_groups(contexts)
    assert sorted(g['members'] for g in actual)==sorted(g['members'] for g in expected)
