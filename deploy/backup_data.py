"""Create a consistent SQLite backup. No deletes or service mutations."""
import argparse
import sqlite3
from pathlib import Path


def backup(source,destination):
    source,destination = Path(source).resolve(),Path(destination).resolve()
    if not source.is_file() or destination.exists() or source == destination:
        raise ValueError('Source must exist and destination must be a new file')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src:
        with sqlite3.connect(destination) as dst:
            src.backup(dst)
            if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError('Backup integrity check failed')


def backup_project(source,destination):
    source,destination=Path(source).resolve(),Path(destination).resolve()
    access=source.with_suffix('.access.sqlite')
    target=destination.with_suffix('.access.sqlite')
    if not source.is_file() or destination.exists() or target.exists():
        raise ValueError('Use existing source and a new backup pair')
    # Snapshot bindings first. Charts are immutable and cannot be deleted, so every
    # referenced report already exists in the following chart snapshot.
    if access.is_file():
        backup(access,target)
    backup(source,destination)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True)
    parser.add_argument('--destination',required=True)
    args=parser.parse_args()
    backup_project(args.source,args.destination)
    print('Chart and access backups created and integrity checked. Keep both files together.')
