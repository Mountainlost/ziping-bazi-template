"""Windows/Linux production supervisor. Reads deploy config; never accesses NØTA state."""
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time


def load_config(path):
    path = Path(path).resolve()
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    for key in ('projectRoot','pythonExecutable','nodeExecutable','dataDirectory','logDirectory'):
        if not Path(config[key]).is_absolute():
            raise ValueError(f'{key} must be an absolute path')
    for key in ('apiHost','webHost'):
        if config[key] != '127.0.0.1':
            raise ValueError('Production app services must bind loopback; expose only the authenticated HTTPS proxy')
    ports = [int(config['apiPort']),int(config['webPort'])]
    if len(set(ports)) != 2 or any(p < 1024 or p > 65535 for p in ports):
        raise ValueError('Use two distinct nonprivileged ports')
    for key in ('pythonExecutable','nodeExecutable'):
        if not Path(config[key]).is_file():
            raise ValueError(f'{key} does not exist')
    root = Path(config['projectRoot'])
    if not (root/'apps/web/.next/standalone/server.js').is_file():
        raise ValueError('Production build missing; run prepare-server.ps1 first')
    return config


def ensure_free(config):
    for key in ('apiPort','webPort'):
        with socket.socket() as check:
            if check.connect_ex(('127.0.0.1',int(config[key]))) == 0:
                raise RuntimeError(f'{key} already in use; existing service was not changed')


def launch_specs(config):
    root = Path(config['projectRoot'])
    env = {k:v for k,v in os.environ.items() if not k.startswith(('MAGPIE_','OPENAI_'))}
    env.update({'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8', 'NEXT_TELEMETRY_DISABLED':'1',
                'BAZI_DB_PATH':str(Path(config['dataDirectory'])/'charts.sqlite'),
                'API_BASE_URL':f'http://127.0.0.1:{config["apiPort"]}', 'NODE_ENV':'production',
                'PORT':str(config['webPort']), 'HOSTNAME':'127.0.0.1'})
    private = Path(config.get('environmentFile',''))
    if private.is_file():
        values = json.loads(private.read_text(encoding='utf-8-sig'))
        if set(values) - {'MAGPIE_CONFIG_FILE'}:
            raise ValueError('Unexpected private environment fields')
        if any(not isinstance(v,str) for v in values.values()):
            raise ValueError('Private environment values must be strings')
        env.update(values)
    api_env=env.copy()
    if config.get('magpieConfigFile'):
        api_env['MAGPIE_CONFIG_FILE']=config['magpieConfigFile']
    api_env['BAZI_PUBLIC_ORIGIN']=config.get('publicOrigin','')
    web_env={k:v for k,v in env.items() if not k.startswith(('MAGPIE_','OPENAI_'))}
    return [
        ('api',[config['pythonExecutable'],'-m','uvicorn','app.main:app','--app-dir',str(root/'apps/api'),
                '--host','127.0.0.1','--port',str(config['apiPort']),'--no-access-log'],root,api_env),
        ('web',[config['nodeExecutable'],str(root/'apps/web/.next/standalone/server.js')],root/'apps/web',web_env)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--check',action='store_true',help='Validate files/config without starting or changing services')
    args = parser.parse_args()
    config = load_config(args.config)
    specs = launch_specs(config)
    if args.check:
        print('Configuration and production files verified; no server started.')
        return
    ensure_free(config)
    Path(config['dataDirectory']).mkdir(parents=True,exist_ok=True)
    log_root = Path(config['logDirectory']); log_root.mkdir(parents=True,exist_ok=True)
    logger = logging.getLogger('ziping-supervisor'); logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_root/'supervisor.log',maxBytes=1_000_000,backupCount=3,encoding='utf-8')
    logger.addHandler(handler)
    children, handles = {}, {}
    stopping = False
    def stop(signum,frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGINT,stop)
    signal.signal(signal.SIGTERM,stop)
    attempts = {name:0 for name,*_ in specs}
    try:
        while not stopping:
            for name,command,cwd,env in specs:
                if name not in children or children[name].poll() is not None:
                    if name in children:
                        attempts[name] += 1
                        if attempts[name] >= 5:
                            raise RuntimeError(f'{name} exited repeatedly; inspect its private log')
                        time.sleep(min(attempts[name]*2,8))
                    if name not in handles:
                        handles[name] = open(log_root/f'{name}-{time.strftime("%Y%m%d-%H%M%S")}.log','ab',buffering=0)
                    children[name] = subprocess.Popen(command,cwd=cwd,env=env,stdin=subprocess.DEVNULL,
                        stdout=handles[name],stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                    logger.info('%s started pid=%s',name,children[name].pid)
            time.sleep(1)
    finally:
        for child in children.values():
            if child.poll() is None:
                child.terminate()
        for child in children.values():
            try: child.wait(timeout=10)
            except subprocess.TimeoutExpired: child.kill()
        for handle in handles.values(): handle.close()


if __name__ == '__main__':
    main()
