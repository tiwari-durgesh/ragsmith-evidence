from ragsmith.core import ingest,search,connect

def test_ingest_and_reingest(tmp_path):
    f=tmp_path/'report.txt'; f.write_text('Revenue was 145 million in 2025.',encoding='utf-8')
    db=tmp_path/'evidence.db'
    a=ingest(f,db); b=ingest(f,db)
    assert a['document_id']==b['document_id']
    assert len(search(db,'revenue'))==1
    connection=connect(db)
    assert connection.execute('SELECT count(*) FROM evidence').fetchone()[0]==1
    connection.close()

def test_xlsx_provenance(tmp_path):
    from openpyxl import Workbook
    w=Workbook(); w.active.title='Finance'; w.active.append(['Metric','2025']); w.active.append(['Revenue',145])
    f=tmp_path/'finance.xlsx'; w.save(f)
    db=tmp_path/'evidence.db'; ingest(f,db)
    connection=connect(db)
    kind,locator=connection.execute('SELECT kind,locator FROM evidence').fetchone()
    connection.close()
    assert (kind,locator)==('table_row','sheet:Finance/row:2')
