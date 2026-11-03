"""Offline-only master pass issuance. Never exposed through an HTTP endpoint."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps/api'))
from app.access import PassStore

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--database',required=True,help='Absolute path to the production charts.access.sqlite')
    parser.add_argument('--universal',action='store_true',help='Issue a private pass reusable across confirmed charts')
    args=parser.parse_args()
    path=Path(args.database)
    if not path.is_absolute() or not path.is_file():
        parser.error('Use an existing absolute access database; start the app once first.')
    print(PassStore(path).issue(kind='universal' if args.universal else 'master'))
