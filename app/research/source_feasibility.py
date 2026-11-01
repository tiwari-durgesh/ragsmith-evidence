"""LAST-step source-only feasibility count. Never decode upstream questions.

Counts are source/group leads, not authored questions, selected cases or labels.
No inference, selection, calibration, network, retry or source modification.
"""

import argparse
from collections import Counter,defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from app.research.selection import source_groups
from scripts.tatqa_excerpt_ingestion import adapt_table,canonical,digest,normalize

TRAIN_SHA256='2df6e722cdbaaa37efcbfb280f5c9a15be29a6ec18f618ef936fe63cc6d07c69'
TRAIN_BYTES=12845647


class SourceProjector:
    """Selective JSON parser: decode allowlisted source values, skip all others.

    Raw bytes are hashed/read, but skipped question/answer values are never passed
    to json's decoder or materialized as Python question objects. No gold loader.
    """
    def __init__(self,text):
        self.text,self.i=text,0
        self.decoder=json.JSONDecoder()
        self.skipped_fields=0

    def ws(self):
        while self.i<len(self.text) and self.text[self.i].isspace():self.i+=1

    def expect(self,char):
        self.ws()
        if self.i>=len(self.text) or self.text[self.i]!=char:raise ValueError('Malformed source JSON structure')
        self.i+=1

    def value(self):
        self.ws();v,end=self.decoder.raw_decode(self.text,self.i);self.i=end
        return v

    def skip(self):
        self.ws();start=self.i
        if start>=len(self.text):raise ValueError('Truncated skipped JSON value')
        opening=self.text[start]
        if opening in '[{':
            stack=[opening];self.i+=1;quoted=False;escaped=False
            while self.i<len(self.text):
                c=self.text[self.i];self.i+=1
                if quoted:
                    if escaped:escaped=False
                    elif c=='\\':escaped=True
                    elif c=='"':quoted=False
                elif c=='"':quoted=True
                elif c in '[{':stack.append(c)
                elif c in ']}':
                    if not stack or (stack.pop(),c) not in {('[',']'),('{','}')}:raise ValueError('Malformed skipped JSON container')
                    if not stack:return
            raise ValueError('Unterminated skipped JSON container')
        if opening=='"':
            self.i+=1;escaped=False
            while self.i<len(self.text):
                c=self.text[self.i];self.i+=1
                if escaped:escaped=False
                elif c=='\\':escaped=True
                elif c=='"':return
            raise ValueError('Unterminated skipped JSON string')
        while self.i<len(self.text) and self.text[self.i] not in ',]} \t\r\n':self.i+=1
        if not re.fullmatch(r'true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?',self.text[start:self.i]):
            raise ValueError('Malformed skipped primitive')

    def object(self,handlers):
        self.expect('{');out={};seen=set();self.ws()
        if self.text[self.i]=='}':self.i+=1;return out
        while True:
            key=self.value()
            if not isinstance(key,str) or key in seen:raise ValueError('Invalid or duplicate object key')
            seen.add(key);self.expect(':')
            if key in handlers:out[key]=handlers[key]()
            else:self.skipped_fields+=1;self.skip()
            self.ws()
            if self.i>=len(self.text):raise ValueError('Truncated source object')
            if self.text[self.i]=='}':self.i+=1;return out
            self.expect(',')

    def array(self,read):
        self.expect('[');out=[];self.ws()
        if self.text[self.i]==']':self.i+=1;return out
        while True:
            out.append(read());self.ws()
            if self.i>=len(self.text):raise ValueError('Truncated source array')
            if self.text[self.i]==']':self.i+=1;return out
            self.expect(',')

    def context(self):
        raw=self.object({'table':lambda:self.object({'uid':self.value,'table':self.value}),
            'paragraphs':lambda:self.array(lambda:self.object({'text':self.value}))})
        table=raw['table'];uid=table['uid'];cells=table['table']
        paragraphs=[p['text'] for p in raw.get('paragraphs',[])]
        if (not isinstance(uid,str) or not uid or not isinstance(cells,list) or not cells
            or any(not isinstance(row,list) or any(not isinstance(c,str) for c in row) for row in cells)
            or any(not isinstance(p,str) for p in paragraphs)):
            raise ValueError('Unsupported source context format')
        return {'context_id':uid,'table':cells,'paragraphs':paragraphs}

    def parse(self):
        contexts=self.array(self.context);self.ws()
        if self.i!=len(self.text):raise ValueError('Trailing source JSON')
        if len({c['context_id'] for c in contexts})!=len(contexts):raise ValueError('Duplicate source UID')
        return contexts


def project_file(path:Path,expected_sha256:str):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('Pinned source checksum mismatch')
    parser=SourceProjector(raw.decode('utf-8'))
    contexts=parser.parse()
    return contexts,{'sha256':expected_sha256,'bytes':len(raw),'source_contexts':len(contexts),
                     'question_answer_values_decoded':0,'source_projection_sha256':digest(contexts)}


def count_sources(contexts:list[dict],exclusion_registry:dict):
    family_ids={r['family_id'] for r in exclusion_registry['family_exclusions']}
    entries=exclusion_registry['context_exclusions']
    pilot_rows=[r for r in entries if 'exact pilot context UID' in r['reason']]
    if len(pilot_rows)!=9 or len(family_ids)!=8:raise ValueError('Complete nine-context/eight-family registry required')
    pilots={r['context_id']:r.get('report_family') for r in pilot_rows}
    source={c['context_id']:c for c in contexts}
    if not set(pilots)<=set(source):raise ValueError('Missing pilot source context; stop')
    enriched=[{**c,**({'report_family':pilots[c['context_id']]} if c['context_id'] in pilots else {})} for c in contexts]
    byid={c['context_id']:c for c in enriched}
    groups,ledger=source_groups(enriched,[byid[u] for u in pilots],family_ids=family_ids,
                               excluded_context_ids={r['context_id'] for r in entries})
    usable=[g for g in groups if not g['excluded']]
    partial_leads=0;unit_bound_partial_leads=0;within_conflicts=0;cross_conflicts=0;unsupported=0
    for group in usable:
        numeric=[];within=defaultdict(set);cross=defaultdict(set)
        for uid in group['members']:
            c=byid[uid]
            try:adapted=adapt_table(uid,c['table'],paragraphs=c.get('paragraphs',[]))
            except ValueError:unsupported+=1;continue
            for e in adapted.evidence:
                if e.kind!='table_row':continue
                match=re.fullmatch(r'Metric: (.+); (\d{4}): (.+)',e.content)
                if not match:continue
                metric,year,value=match.groups();meta=e.metadata or {}
                key=(normalize(metric),year,normalize(meta.get('unit','')),meta.get('currency_marker',''),meta.get('section',''))
                numeric.append((uid,key,Decimal(value)))
                within[(uid,key)].add(Decimal(value));cross[key].add(Decimal(value))
        if len({(uid,key) for uid,key,v in numeric})>=2:partial_leads+=1
        if len({(uid,key) for uid,key,v in numeric if key[2]})>=2:unit_bound_partial_leads+=1
        if any(len(v)>1 for v in within.values()):within_conflicts+=1
        if any(len(v)>1 for v in cross.values()):cross_conflicts+=1
    reasons=Counter(rule.split(':')[0] for row in ledger for rule in row['rules'])
    enough_groups=len(usable)>=10
    report={'source_contexts':len(contexts),'source_groups':len(groups),
            'excluded_contexts':len(ledger),'excluded_groups':sum(g['excluded'] for g in groups),
            'surviving_contexts':sum(len(g['members']) for g in usable),'surviving_groups':len(usable),
            'exclusion_rule_context_counts':dict(sorted(reasons.items())),
            'groups_with_at_least_two_canonical_fact_leads':partial_leads,
            'groups_with_two_explicit_unit_bound_fact_leads':unit_bound_partial_leads,
            'groups_with_within_context_numeric_discrepancy_leads':within_conflicts,
            'groups_with_groupwide_numeric_discrepancy_leads':cross_conflicts,
            'surviving_contexts_unsupported_by_adapter':unsupported,
            'certified_genuine_partial_opportunities':0,'certified_genuine_conflict_opportunities':0,
            'genuine_opportunity_count_status':'not certified; lead counts do not establish source scope, absence, entity, units or resolving version/definition priority',
            'required_evaluation':{'partial':9,'conflict':4,'groups':6},
            'required_development':{'partial':6,'conflict':3,'groups':4},
            'joint_group_capacity_at_least_ten':enough_groups,
            'stop_required':True,
            'stop_reason':('Fewer than ten nonquarantined source groups' if not enough_groups else
                           'Genuine partial/conflict quotas and joint no-reused-fact capacity not certified by source-only leads'),
            'selection_performed':False,'questions_decoded':0,'labels_created':False,
            'group_graph_sha256':digest(groups),'exclusion_ledger_sha256':digest(ledger),
            'notice':'Count only. No source groups are independent reports; unresolved hidden report overlap remains accepted.'}
    return report,ledger


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--exclusions',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.source.name!='tatqa_dataset_train.json' or args.output.exists():raise ValueError('Pinned training source and fresh output directory required')
        contexts,provenance=project_file(args.source,TRAIN_SHA256)
        if provenance['bytes']!=TRAIN_BYTES:raise ValueError('Pinned source size mismatch')
        registry=json.loads(args.exclusions.read_text(encoding='utf-8'))
        if registry['source_sha256']!=TRAIN_SHA256:raise ValueError('Exclusion registry source mismatch')
        report,ledger=count_sources(contexts,registry)
        report['source_provenance']=provenance
        report['exclusion_registry_sha256']=hashlib.sha256(args.exclusions.read_bytes()).hexdigest()
        report['count_tool_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        args.output.mkdir(parents=True)
        (args.output/'aggregate.json').write_bytes(canonical(report))
        (args.output/'private-source-exclusions.json').write_bytes(canonical(ledger))
        print(json.dumps(report,indent=2,allow_nan=False))
    except (ValueError,OSError,KeyError,TypeError,IndexError) as exc:parser.error(str(exc))


if __name__=='__main__':main()
