"""Explicit-file provisional label sheets, validation, locks and agreement.

No automatic labeler, source selection, API or calibration. Completed files are
private. Source-only sheets omit assigned strata, model outputs and other labels.
"""

import argparse
from collections import Counter
from decimal import Decimal
import json
from pathlib import Path

from app.research.corpus_runner import Corpus, StudyRequest
from scripts.tatqa_excerpt_ingestion import canonical, digest, normalize, numeric_value, name_tokens

STATUSES={"supported","missing","contradicted","unverified","not_adjudicable"}
PROVISIONAL="provisional, single-annotator"


def make_sheet(corpus: Corpus, requests: list[StudyRequest], *, partition: str, data_origin: str) -> dict:
    if partition not in {"development","evaluation","practice"} or data_origin not in {"synthetic","pilot","new-study"}:
        raise ValueError("Explicit partition and data origin required")
    if len({r.case_id for r in requests})!=len(requests):raise ValueError("Duplicate requests")
    corpus.verify();cases=[]
    for request in requests:
        contexts=[]
        for uid in request.context_ids:
            entry=corpus.contexts[uid]
            if entry['group_id']!=request.group_id:raise ValueError("Scope crosses groups")
            source=json.loads(Path(entry['source_path']).read_text(encoding='utf-8'))
            contexts.append({"context_id":uid,"source_sha256":entry['version'],"source":source})
        cases.append({"case_id":request.case_id,"question":request.question,
            "requested_facts":[r.model_dump() for r in request.requested_facts],"contexts":contexts,
            "labels":[{"requirement_id":r.requirement_id,"status":"","raw_values":[],"cells":[],"unit":"","notes":"",
                       "absence_scan":{"terms":sorted({r.metric,*name_tokens(r.metric),str(r.year)}),
                                       "context_ids":sorted(request.context_ids),"all_rows_and_paragraphs":False}}
                      for r in request.requested_facts]})
    sheet={"schema_version":"study-labels-v1","partition":partition,"data_origin":data_origin,
           "corpus_sha256":corpus.sha256,"selection_sha256":digest([r.case_id for r in requests]),
           "label_status":PROVISIONAL,"metadata":{"annotator_id":"","annotator_kind":"human",
                        "independent":False,"elapsed_minutes":""},"cases":cases}
    sheet['input_sha256']=digest(immutable(sheet))
    return sheet


def immutable(sheet):
    return {k:v for k,v in sheet.items() if k not in {'cases','metadata','input_sha256'}}|{
        "cases":[{k:v for k,v in c.items() if k!='labels'}|{
            "label_requirement_ids":[x['requirement_id'] for x in c['labels']]} for c in sheet['cases']]}


def _no_null(value):
    if value is None:raise ValueError("Null label fields are not permitted")
    if isinstance(value,dict):
        for v in value.values():_no_null(v)
    elif isinstance(value,list):
        for v in value:_no_null(v)


def validate_sheet(sheet: dict, template: dict) -> None:
    _no_null(sheet)
    if (sheet.get('schema_version')!='study-labels-v1' or sheet.get('partition') not in {'development','evaluation','practice'}
        or sheet.get('data_origin') not in {'synthetic','pilot','new-study'}):
        raise ValueError("Invalid label-sheet schema/partition/origin")
    if set(sheet)!=set(template) or immutable(sheet)!=immutable(template):
        raise ValueError("Source, question, scope, requirements or metadata schema changed")
    if sheet.get('input_sha256')!=digest(immutable(template)) or template.get('input_sha256')!=digest(immutable(template)):
        raise ValueError("Frozen sheet input hash mismatch")
    if sheet.get('label_status')!=PROVISIONAL:raise ValueError("Labels must stay provisional")
    metadata=sheet['metadata']
    if set(metadata)!={'annotator_id','annotator_kind','independent','elapsed_minutes'}:
        raise ValueError("Unexpected annotator metadata")
    if (not isinstance(metadata['annotator_id'],str) or not metadata['annotator_id'].strip()
        or metadata['annotator_kind'] not in {'human','synthetic'} or metadata['independent'] is not True
        or type(metadata['elapsed_minutes']) not in (int,float) or not 0<=metadata['elapsed_minutes']<1_000_000):
        raise ValueError("Complete independent annotator metadata required")
    for case in sheet['cases']:
        sources={s['context_id']:s for s in case['contexts']}
        if len(sources)!=len(case['contexts']) or any(digest(s['source'])!=s['source_sha256'] or
             s['source']['context_id']!=s['context_id'] for s in sources.values()):
            raise ValueError("Source snapshot hash/identity mismatch")
        facts=case['requested_facts']
        if len(case['labels'])!=len(facts):raise ValueError("Every requirement must be labeled")
        for fact,label in zip(facts,case['labels']):
            if set(label)!={'requirement_id','status','raw_values','cells','unit','notes','absence_scan'}:
                raise ValueError("Unexpected label fields; no conditions or outputs permitted")
            if label['requirement_id']!=fact['requirement_id'] or label['status'] not in STATUSES:
                raise ValueError("Requirement or allowed status mismatch")
            if not all(isinstance(label[k],str) and label[k].strip() for k in ('notes','unit')):
                raise ValueError("Source-based notes and explicit unit/unclear required")
            values=label['raw_values'];cells=label['cells'];status=label['status']
            if not isinstance(values,list) or any(not isinstance(v,str) or numeric_value(v) is None for v in values):
                raise ValueError("Values must be raw unambiguous numeric strings")
            if not isinstance(cells,list):raise ValueError("Cells must be a list")
            raw=[]
            for cell in cells:
                if set(cell)!={'context_id','row','column'} or cell['context_id'] not in sources:
                    raise ValueError("Cell outside fixed source scope")
                source=sources[cell['context_id']]['source'];table=source['table']
                row,col=cell['row'],cell['column']
                if type(row) is not int or type(col) is not int or not 1<=row<=len(table) or not 1<=col<=len(table[row-1]):
                    raise ValueError("Invalid one-based source cell")
                raw.append(table[row-1][col-1])
                if status in {'supported','contradicted'} and source['unit'] and label['unit']!=source['unit']:
                    raise ValueError("Cited source unit differs; do not convert units")
            if any(v not in raw for v in values):raise ValueError("Value must be copied from a cited original cell")
            distinct={Decimal(numeric_value(v)) for v in values}
            if status=='supported' and (len(distinct)!=1 or not cells or label['unit']=='unclear'):
                raise ValueError("Supported requires an unambiguous value, unit and cell")
            if status=='contradicted' and (len(distinct)<2 or not cells or label['unit']=='unclear'):
                raise ValueError("Contradiction requires distinct numeric values, same unit and source cells")
            if status=='missing' and (values or cells):raise ValueError("Missing has no returned value or supporting cell")
            if status in {'unverified','not_adjudicable'} and values:
                raise ValueError("Uncertain requirements cannot be numeric gold")
            scan=label['absence_scan']
            if not isinstance(scan,dict) or set(scan)!={'terms','context_ids','all_rows_and_paragraphs'}:
                raise ValueError("Explicit absence scan fields required")
            if (not isinstance(scan['terms'],list) or not all(isinstance(x,str) for x in scan['terms'])
                or not isinstance(scan['context_ids'],list) or not all(isinstance(x,str) for x in scan['context_ids'])
                or not set(scan['context_ids'])<=set(sources) or type(scan['all_rows_and_paragraphs']) is not bool):
                raise ValueError("Invalid absence scan types/scope")
            if status=='missing':
                expected={normalize(fact['metric']),*name_tokens(fact['metric']),str(fact['year'])}
                if (not isinstance(scan['terms'],list) or not all(isinstance(x,str) for x in scan['terms']) or
                    not expected<={normalize(x) for x in scan['terms']} or scan['all_rows_and_paragraphs'] is not True or
                    sorted(scan['context_ids'])!=sorted(sources)):
                    raise ValueError("Missing requires exhaustive keyword/year/all-context table and paragraph scan")


def lock_sheet(sheet, template, path: Path):
    validate_sheet(sheet,template)
    lock={"locked":True,"labels_sha256":digest(sheet),"template_sha256":digest(template),
          "input_sha256":sheet['input_sha256'],"partition":sheet['partition'],
          "selection_sha256":sheet['selection_sha256'],"label_status":PROVISIONAL}
    envelope={"labels":sheet,"lock":lock}
    with path.open('xb') as stream:stream.write(canonical(envelope))
    return envelope


def verify_lock(envelope):
    sheet,lock=envelope['labels'],envelope['lock']
    if (lock.get('locked') is not True or lock.get('labels_sha256')!=digest(sheet)
        or lock.get('input_sha256')!=sheet.get('input_sha256') or lock.get('partition')!=sheet.get('partition')
        or lock.get('selection_sha256')!=sheet.get('selection_sha256')):
        raise ValueError("Locked-label receipt mismatch")
    validate_sheet(sheet,sheet)
    return sheet


def agreement(first,second):
    a,b=verify_lock(first),verify_lock(second)
    if a['input_sha256']!=b['input_sha256']:raise ValueError("Different source/question sheets")
    if a['metadata']['annotator_id']==b['metadata']['annotator_id']:raise ValueError("Distinct independent annotators required")
    left=[(c['case_id'],x['requirement_id'],x['status']) for c in a['cases'] for x in c['labels']]
    right=[(c['case_id'],x['requirement_id'],x['status']) for c in b['cases'] for x in c['labels']]
    if not left:raise ValueError("No labels to compare")
    n=len(left);observed=sum(x[2]==y[2] for x,y in zip(left,right))/n
    ca,cb=Counter(x[2] for x in left),Counter(x[2] for x in right)
    expected=sum(ca[s]*cb[s] for s in STATUSES)/(n*n)
    return {"requirements":n,"raw_agreement":observed,"cohens_kappa":(observed-expected)/(1-expected) if expected<1 else None,
            "kappa_note":"undefined when expected agreement is one" if expected==1 else "descriptive pre-adjudication categorical agreement",
            "human_annotators_declared":a['metadata']['annotator_kind']==b['metadata']['annotator_kind']=='human',
            "independence":"declared, not established by software","label_status":PROVISIONAL,
            "disagreements":[{"case_id":x[0],"requirement_id":x[1]} for x,y in zip(left,right) if x[2]!=y[2]]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for action in ('validate','lock'):
        p=sub.add_parser(action);p.add_argument('template',type=Path);p.add_argument('labels',type=Path)
        if action=='lock':p.add_argument('output',type=Path)
    p=sub.add_parser('agreement');p.add_argument('first',type=Path);p.add_argument('second',type=Path)
    args=parser.parse_args()
    def read(path):return json.loads(path.read_text(encoding='utf-8'))
    try:
        if args.command=='agreement':print(json.dumps(agreement(read(args.first),read(args.second)),allow_nan=False))
        else:
            sheet,template=read(args.labels),read(args.template)
            if args.command=='validate':validate_sheet(sheet,template);print('Labels valid; no lock written')
            else:print(json.dumps(lock_sheet(sheet,template,args.output)['lock'],allow_nan=False))
    except (ValueError,OSError,KeyError,TypeError) as exc:parser.error(str(exc))


if __name__=='__main__':main()
