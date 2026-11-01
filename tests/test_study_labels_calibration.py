"""Only fabricated annotation returns and development predictions are used."""

import copy
import json
import math

import pytest

from app.research.corpus_runner import Excerpt,StudyRequest,build_corpus
from app.research.labels import make_sheet,validate_sheet,lock_sheet,verify_lock,agreement
from app.research.calibration import calibrate,lock_calibration


def fixture(tmp_path,n=1,partition='practice',origin='synthetic'):
    corpus=build_corpus([Excerpt(context_id='synthetic',group_id='g',unit='USD',
         table=[['Metric','2025'],['Revenue','10'],['Cash','4']])],tmp_path/'corpus')
    requests=[StudyRequest(case_id=f'synthetic-{i:02}',question='Give Revenue and Cash in 2025.',group_id='g',context_ids=['synthetic'],
        requested_facts=[{'requirement_id':'r','metric':'Revenue','year':2025},{'requirement_id':'c','metric':'Cash','year':2025}]) for i in range(n)]
    template=make_sheet(corpus,requests,partition=partition,data_origin=origin)
    sheet=copy.deepcopy(template)
    sheet['metadata'].update(annotator_id='synthetic-reviewer-A',annotator_kind='synthetic',independent=True,elapsed_minutes=1)
    for c in sheet['cases']:
        for i,label in enumerate(c['labels']):
            label.update(status='supported',raw_values=['10' if i==0 else '4'],
                         cells=[{'context_id':'synthetic','row':i+2,'column':2}],unit='USD',notes='Invented test annotation')
    return corpus,template,sheet


def predictions(corpus,sheet):
    version=corpus.contexts['synthetic']['version']
    return [{'case_id':c['case_id'],'failed':False,'claims':[
        {'requirement_id':r['requirement_id'],'value':r['raw_values'][0],'confidence':.8,
         'citations':[{'locator':f"table:synthetic/row:{i+1}/column:1",'document_version':version}]}
        for i,r in enumerate(c['labels'])]} for c in sheet['cases']]


def test_blinded_sheet_has_no_assigned_condition_outputs_or_other_labels(tmp_path):
    _,template,sheet=fixture(tmp_path)
    assert all(r['status']=='' for c in template['cases'] for r in c['labels'])
    assert not {'stratum','baselines','expected_answer','primary_label'}&set(template['cases'][0])
    validate_sheet(sheet,template)


@pytest.mark.parametrize('change',[
    lambda s:s['cases'][0]['labels'][0].update(status=None),
    lambda s:s['cases'][0]['labels'][0].update(status='full'),
    lambda s:s['cases'][0]['labels'][0].update(raw_values=['999']),
    lambda s:s['cases'][0]['labels'][0].update(cells=[{'context_id':'synthetic','row':99,'column':2}]),
    lambda s:s['cases'][0].update(question='changed'),
    lambda s:s['metadata'].update(independent=False),
])
def test_invalid_or_changed_labels_rejected(tmp_path,change):
    _,template,sheet=fixture(tmp_path);change(sheet)
    with pytest.raises(ValueError):validate_sheet(sheet,template)


def test_missing_requires_full_absence_scan_and_no_claimed_value(tmp_path):
    _,template,sheet=fixture(tmp_path)
    label=sheet['cases'][0]['labels'][0]
    label.update(status='missing',raw_values=[],cells=[],notes='Synthetic exercise; not actual source gold')
    with pytest.raises(ValueError,match='exhaustive'):validate_sheet(sheet,template)
    label['absence_scan']['all_rows_and_paragraphs']=True
    validate_sheet(sheet,template)  # A schema validator does not judge human semantic truth.


def test_lock_refuses_overwrite_and_detects_content_mutation(tmp_path):
    _,template,sheet=fixture(tmp_path)
    lock=lock_sheet(sheet,template,tmp_path/'labels.json')
    assert verify_lock(lock)==sheet
    with pytest.raises(FileExistsError):lock_sheet(sheet,template,tmp_path/'labels.json')
    lock['labels']['cases'][0]['labels'][0]['notes']='tampered'
    with pytest.raises(ValueError,match='receipt'):verify_lock(lock)


def test_agreement_raw_kappa_disagreement_and_no_false_human_claim(tmp_path):
    _,template,a=fixture(tmp_path);b=copy.deepcopy(a)
    b['metadata']['annotator_id']='synthetic-reviewer-B'
    b['cases'][0]['labels'][1].update(status='unverified',raw_values=[])
    report=agreement(lock_sheet(a,template,tmp_path/'a.json'),lock_sheet(b,template,tmp_path/'b.json'))
    assert report['raw_agreement']==.5 and report['cohens_kappa']==0
    assert len(report['disagreements'])==1 and not report['human_annotators_declared']


def test_degenerate_kappa_is_undefined_not_perfect_agreement_claim(tmp_path):
    _,template,a=fixture(tmp_path);b=copy.deepcopy(a);b['metadata']['annotator_id']='B'
    result=agreement(lock_sheet(a,template,tmp_path/'a.json'),lock_sheet(b,template,tmp_path/'b.json'))
    assert result['raw_agreement']==1 and result['cohens_kappa'] is None


def test_fixed_dev_grid_caps_unsafe_questions_and_prefers_higher_threshold(tmp_path):
    corpus,template,sheet=fixture(tmp_path,20,'development')
    locked=lock_sheet(sheet,template,tmp_path/'labels.json');pred=predictions(corpus,sheet)
    for row in pred[:2]:row['claims'][0].update(value='999',confidence=.6)
    result=calibrate(locked,pred,development_selection_sha256=sheet['selection_sha256'])
    assert result['threshold']==.8 and result['locked'] is False
    assert next(r for r in result['trials'] if r['threshold']==.6)['unsafe_questions']==2
    assert result['generation_failure_questions']==0
    receipt=lock_calibration(result,tmp_path/'threshold.json')
    assert receipt['locked'] and receipt['threshold']==.8
    with pytest.raises(FileExistsError):lock_calibration(result,tmp_path/'threshold.json')


def test_always_abstain_fallback_and_generation_failure_denominators(tmp_path):
    corpus,template,sheet=fixture(tmp_path,20,'development')
    locked=lock_sheet(sheet,template,tmp_path/'labels.json');pred=predictions(corpus,sheet)
    for row in pred:
        for c in row['claims']:c.update(value='999',confidence=1.0)
    result=calibrate(locked,pred,development_selection_sha256=sheet['selection_sha256'])
    assert result['threshold']=='always_abstain'
    pred[0].update(claims=[],failed=True)
    result=calibrate(locked,pred,development_selection_sha256=sheet['selection_sha256'])
    assert result['development_questions']==20 and result['generation_failure_questions']==1


@pytest.mark.parametrize('partition,origin,n', [('evaluation','synthetic',20),('development','pilot',20),('development','synthetic',19)])
def test_calibration_rejects_evaluation_pilot_or_wrong_size(tmp_path,partition,origin,n):
    corpus,template,sheet=fixture(tmp_path,n,partition,origin)
    locked=lock_sheet(sheet,template,tmp_path/'labels.json')
    with pytest.raises(ValueError,match='20 locked development'):
        calibrate(locked,predictions(corpus,sheet),development_selection_sha256=sheet['selection_sha256'])


def test_calibration_rejects_nan_confidence_wrong_citation_and_missing_cases(tmp_path):
    corpus,template,sheet=fixture(tmp_path,20,'development')
    locked=lock_sheet(sheet,template,tmp_path/'labels.json');pred=predictions(corpus,sheet)
    pred[0]['claims'][0]['confidence']=math.nan
    with pytest.raises(ValueError,match='confidence'):calibrate(locked,pred,development_selection_sha256=sheet['selection_sha256'])
    pred=predictions(corpus,sheet)
    for row in pred[:2]:row['claims'][0]['citations'][0]['document_version']='wrong'
    result=calibrate(locked,pred,development_selection_sha256=sheet['selection_sha256'])
    assert result['threshold']=='always_abstain'
    with pytest.raises(ValueError,match='every development case'):
        calibrate(locked,pred[:-1],development_selection_sha256=sheet['selection_sha256'])
