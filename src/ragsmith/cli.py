import argparse
import json
import sqlite3
from pathlib import Path
from ragsmith.core import SUPPORTED, ingest, search

def main():
    parser = argparse.ArgumentParser(description='RAGSmith-Evidence pilot CLI')
    parser.add_argument('--db',type=Path,default=Path('data/processed/evidence.db'))
    sub = parser.add_subparsers(dest='command',required=True)
    sub.add_parser('ingest-dir').add_argument('directory',type=Path)
    sub.add_parser('ingest').add_argument('path',type=Path)
    sub.add_parser('search').add_argument('query')
    ask = sub.add_parser('ask', help='Assess explicit metric/year requirements')
    ask.add_argument('request', type=Path)
    ask.add_argument('--lookup-config', type=Path)
    ask.add_argument('--top-k', type=int, default=10)
    ask.add_argument('--format', choices=('json', 'text'), default='json')
    args = parser.parse_args()
    if args.command == 'ask':
        from ragsmith.lookup_config import LookupConfig
        from ragsmith.retrieval import RetrievalConfig, answer_from_database
        from ragsmith.value_lookup import LookupQuestion

        try:
            request = LookupQuestion.from_payload(json.loads(
                args.request.read_text(encoding='utf-8')
            ))
            config = (
                LookupConfig.from_file(args.lookup_config)
                if args.lookup_config else LookupConfig()
            )
            result = answer_from_database(
                args.db, request, config, RetrievalConfig(args.top_k)
            )
        except (OSError, ValueError, sqlite3.Error) as exc:
            parser.error(str(exc))
        if args.format == 'text':
            print(result['response']['text'])
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    if args.command == 'search':
        print(json.dumps(search(args.db,args.query),indent=2,ensure_ascii=False)); return
    files = [args.path] if args.command == 'ingest' else sorted(f for f in args.directory.rglob('*') if f.is_file() and f.suffix.lower() in SUPPORTED)
    for file in files:
        try: print(json.dumps(ingest(file,args.db,Path('data/manifests/ingestion.jsonl')),indent=2))
        except Exception as exc: print(f'ERROR {file}: {exc}')

if __name__ == '__main__': main()
