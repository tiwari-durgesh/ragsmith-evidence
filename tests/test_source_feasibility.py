"""Source-only parser/count tests. No real source file opened by pytest."""

import hashlib
import json

import pytest

from app.research.source_feasibility import SourceProjector,project_file,count_sources


def raw(uid='context',value='10'):
    return {'table':{'uid':uid,'table':[['Metric','2025'],['Revenue',value],['Cash','4']]},
            'paragraphs':[{'uid':'p','order':1,'text':'Synthetic source paragraph'}],
            'questions':[{'question':'NEVER DECODE THIS QUESTION','answer':{'secret':['NEVER DECODE THIS ANSWER','\\"}[]']}}]}


def test_projection_never_decodes_or_materializes_question_answer_values():
    parser=SourceProjector(json.dumps([raw()],ensure_ascii=False))
    decoder=parser.decoder;decoded=[]
    class Spy:
        def raw_decode(self,*args):
            value,end=decoder.raw_decode(*args);decoded.append(value);return value,end
    parser.decoder=Spy()
    result=parser.parse()
    assert result[0]['paragraphs']==['Synthetic source paragraph']
    assert 'NEVER DECODE' not in str(result) and 'NEVER DECODE' not in str(decoded)
    assert parser.skipped_fields>=2


def test_question_changes_leave_source_projection_hash_unchanged(tmp_path):
    hashes=[]
    for i in range(2):
        r=raw();r['questions']=[{'question':'different hidden question '*i}]
        content=json.dumps([r]).encode();path=tmp_path/f'{i}.json';path.write_bytes(content)
        contexts,metadata=project_file(path,hashlib.sha256(content).hexdigest())
        hashes.append(metadata['source_projection_sha256'])
        assert metadata['question_answer_values_decoded']==0
    assert hashes[0]==hashes[1]
    with pytest.raises(ValueError,match='checksum'):project_file(path,'0'*64)


@pytest.mark.parametrize('text',['[','[{"table":','[] trailing','[{"table":{},"table":{}}]'])
def test_truncated_or_duplicate_source_structure_stops(text):
    with pytest.raises((ValueError,KeyError,IndexError)):SourceProjector(text).parse()


def test_count_outputs_only_aggregate_leads_and_conservative_stop():
    contexts=[{'context_id':f'pilot-{i}','table':[[f'P{i}','2025'],['A',str(i+1)]],'paragraphs':[]} for i in range(9)]
    contexts += [{'context_id':'unrelated','table':[['Different','2024'],['B','17'],['C','19']],'paragraphs':[]}]
    registry={'context_exclusions':[{'context_id':f'pilot-{i}','reason':'exact pilot context UID','report_family':f'f-{i%8}'} for i in range(9)],
              'family_exclusions':[{'family_id':f'f-{i}'} for i in range(8)]}
    report,ledger=count_sources(contexts,registry)
    assert report['questions_decoded']==0 and report['selection_performed'] is False
    assert report['stop_required'] and report['surviving_groups']<10
    assert not any(isinstance(v,list) for v in report.values())
    assert report['certified_genuine_conflict_opportunities']==0
    assert len(ledger)>=9
