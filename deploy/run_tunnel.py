"""Dedicated reconnecting reverse SSH tunnel; never controls another service."""
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import signal
import socket
import subprocess
import threading
import time


def command(config):
    for field in ('identityFile','knownHostsFile'):
        if not Path(config[field]).is_absolute() or not Path(config[field]).is_file():
            raise ValueError(f'{field} must be an existing absolute path')
    for field in ('sshPort','remotePort','localPort'):
        if not isinstance(config[field],int) or not 1<=config[field]<=65535:
            raise ValueError(f'Invalid {field}')
    if config['remotePort']<1024 or config['localPort']<1024:
        raise ValueError('Tunnel must use dedicated nonprivileged ports')
    if not config['host'] or config['host'].startswith('-') or not config['username'] or config['username'].startswith('-'):
        raise ValueError('Invalid SSH destination')
    return ['ssh','-NT','-i',config['identityFile'],'-o','BatchMode=yes','-o','IdentitiesOnly=yes',
            '-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+config['knownHostsFile'],
            '-o','ExitOnForwardFailure=yes','-o','ServerAliveInterval=20','-o','ServerAliveCountMax=3',
            '-o','ConnectTimeout=10','-R',f'127.0.0.1:{config["remotePort"]}:127.0.0.1:{config["localPort"]}',
            '-p',str(config['sshPort']),'-l',config['username'],config['host']]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    cmd=command(config)
    if args.check:
        print('Dedicated tunnel configuration valid; no connection opened.')
        return
    root=Path(config['logDirectory']);root.mkdir(parents=True,exist_ok=True)
    logger=logging.getLogger('ziping-tunnel');logger.setLevel(logging.INFO)
    logger.addHandler(RotatingFileHandler(root/'tunnel.log',maxBytes=500_000,backupCount=3,encoding='utf-8'))
    stop=threading.Event()
    signal.signal(signal.SIGINT,lambda *_:stop.set())
    signal.signal(signal.SIGTERM,lambda *_:stop.set())
    child=None
    try:
        while not stop.is_set():
            with socket.socket() as check:
                ready=check.connect_ex(('127.0.0.1',config['localPort']))==0
            if not ready:
                stop.wait(5)
                continue
            child=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                   creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            logger.info('Dedicated SSH process started pid=%s',child.pid)
            while child.poll() is None and not stop.wait(1):
                pass
            if not stop.is_set():
                logger.warning('Tunnel exited code=%s; reconnecting in 5 seconds',child.returncode)
                stop.wait(5)
    finally:
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill()


if __name__=='__main__':
    main()
