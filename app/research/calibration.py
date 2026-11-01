"""Development-only fixed-grid calibration. Written/tested, not run on real data.

There is no import-time choice or threshold configuration write. No pilot tuning.
"""

from fractions import Fraction
from pathlib import Path
import re
from decimal import Decimal

from app.research.labels import verify_lock
from scripts.tatqa_excerpt_ingestion import canonical, digest, numeric_value


def predictions_from_batch(batch):
    records=[]
    for result in batch['results']:
        never=next((p for p in result.get('policies',[]) if p['variant']=='never_abstain_retrieve_and_answer'),None)
        claims=[]
        if never:
            bynumber={c['citation_number']:c for c in never['citations']}
            for v in never['values']:
                claims.append({"requirement_id":v['requirement_id'],"value":v['value'],"confidence":v['confidence'],
                               "citations":[bynumber[n] for n in v['citation_numbers']]})
        records.append({"case_id":result['question_id'],"claims":claims,"failed":result['status']!='completed'})
    return records


def calibrate(development_lock: dict, predictions: list[dict], *, development_selection_sha256: str):
    labels=verify_lock(development_lock)
    if labels['partition']!='development' or labels['data_origin']=='pilot' or len(labels['cases'])!=20:
        raise ValueError("Exactly 20 locked development cases required; pilot/evaluation calibration forbidden")
    if labels['selection_sha256']!=development_selection_sha256:
        raise ValueError("Development selection hash mismatch")
    if len({r['case_id'] for r in predictions})!=20 or {r['case_id'] for r in predictions}!={c['case_id'] for c in labels['cases']}:
        raise ValueError("Predictions must cover every development case exactly once")
    bycase={r['case_id']:r for r in predictions}
    for c in labels['cases']:
        if any(r['status'] in {'not_adjudicable','unverified'} for r in c['labels']):
            raise ValueError("Unadjudicable development gold must be resolved before calibration")
        ids={r['requirement_id'] for r in c['labels']};seen=set()
        if type(bycase[c['case_id']].get('failed')) is not bool:raise ValueError("Explicit generation failure flag required")
        for claim in bycase[c['case_id']]['claims']:
            if claim['requirement_id'] not in ids or claim['requirement_id'] in seen:
                raise ValueError("Unexpected or duplicate candidate requirement")
            seen.add(claim['requirement_id'])
            confidence=claim['confidence']
            if type(confidence) not in (int,float) or not 0<=confidence<=1:
                raise ValueError("Invalid raw value-token confidence")
        if len(seen)<len(ids) and not bycase[c['case_id']]['failed']:
            raise ValueError("Missing candidates must remain marked generation failures")
    def supported(case,label,claim):
        if label['status']!='supported' or numeric_value(claim['value']) is None:return False
        if Decimal(numeric_value(claim['value'])) not in {Decimal(numeric_value(v)) for v in label['raw_values']}:return False
        contexts={s['context_id']:s for s in case['contexts']}
        expected={(c['context_id'],c['row'],c['column']) for c in label['cells']}
        cites=claim['citations']
        if not cites:return False
        # Every emitted reference must map to a reviewed supporting original cell.
        for cite in cites:
            match=re.fullmatch(r'table:(.+)/row:(\d+)/column:(\d+)',cite.get('locator',''))
            if not match:return False
            uid,row,col=match.group(1),int(match.group(2))+1,int(match.group(3))+1
            if (uid,row,col) not in expected or cite.get('document_version')!=contexts[uid]['source_sha256']:
                return False
            if cite.get('unit',label['unit'])!=label['unit']:return False
        return True
    grid=[i/10 for i in range(11)]+['always_abstain']
    trials=[]
    for threshold in grid:
        unsafe=0;coverages=[]
        for case in labels['cases']:
            gold={r['requirement_id']:r for r in case['labels']}
            claims=[] if threshold=='always_abstain' else [c for c in bycase[case['case_id']]['claims'] if c['confidence']>=threshold]
            correct={c['requirement_id'] for c in claims if supported(case,gold[c['requirement_id']],c)}
            unsafe+=any(not supported(case,gold[c['requirement_id']],c) for c in claims)
            total=sum(r['status']=='supported' for r in gold.values())
            if total:coverages.append(Fraction(len(correct),total))
        coverage=sum(coverages,Fraction())/len(coverages) if coverages else Fraction()
        trials.append({"threshold":threshold,"unsafe_questions":unsafe,"macro_supported_coverage":float(coverage),
                       "coverage_fraction":[coverage.numerator,coverage.denominator],"feasible":unsafe<=1})
    def key(row):
        n,d=row['coverage_fraction']
        return (Fraction(n,d),-row['unsafe_questions'],2 if row['threshold']=='always_abstain' else row['threshold'])
    chosen=max((r for r in trials if r['feasible']),key=key)
    return {"locked":False,"threshold":chosen['threshold'],"development_selection_sha256":development_selection_sha256,
            "development_labels_sha256":digest(labels),"predictions_sha256":digest(predictions),"grid":grid,
            "trials":trials,"decision_rule":"maximize macro supported requirement coverage; <=1 unsafe question; ties fewer unsafe, higher threshold",
            "data_origin":labels['data_origin'],"provisional":True,
            "development_questions":20,"generation_failure_questions":sum(r['failed'] for r in predictions),
            "notice":"Development estimate only; not a calibrated probability or safety guarantee."}


def lock_calibration(result: dict, path: Path):
    body={**result,"locked":True}
    receipt={**body,"sha256":digest(body)}
    with path.open('xb') as stream:stream.write(canonical(receipt))
    return receipt
