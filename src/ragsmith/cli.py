import argparse
import json
from pathlib import Path
from ragsmith.core import SUPPORTED, ingest, search

def main():
    parser = argparse.ArgumentParser(description='RAGSmith-Evidence pilot CLI')
    parser.add_argument('--db',type=Path,default=Path('data/processed/evidence.db'))
    sub = parser.add_subparsers(dest='command',required=True)
    sub.add_parser('ingest-dir').add_argument('directory',type=Path)
    sub.add_parser('ingest').add_argument('path',type=Path)
    sub.add_parser('search').add_argument('query')
    args = parser.parse_args()
    if args.command == 'search':
        print(json.dumps(search(args.db,args.query),indent=2,ensure_ascii=False)); return
    files = [args.path] if args.command == 'ingest' else sorted(f for f in args.directory.rglob('*') if f.is_file() and f.suffix.lower() in SUPPORTED)
    for file in files:
        try: print(json.dumps(ingest(file,args.db,Path('data/manifests/ingestion.jsonl')),indent=2))
        except Exception as exc: print(f'ERROR {file}: {exc}')

if __name__ == '__main__': main()
