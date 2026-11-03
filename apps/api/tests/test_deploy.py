import importlib.util
from pathlib import Path
import sqlite3
import pytest

ROOT=Path(__file__).resolve().parents[3]


def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'deploy'/f'{name}.py')
    item=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item


def test_consistent_backup_preserves_locked_chart(tmp_path):
    from app.storage import ChartStore
    src=tmp_path/'data/charts.sqlite'
    store=ChartStore(src)
    chart={'id':'backup-test','locked':False,'pillars':{'day':'庚辰'}}
    store.add(chart)
    chart['locked']=True
    before=store.freeze(chart)
    destination=tmp_path/'backup/charts.sqlite'
    module('backup_data').backup(src,destination)
    recovered=ChartStore(destination)
    assert recovered.get(chart['id'],True)==before
    with recovered.connect() as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('DELETE FROM charts')
    with pytest.raises(ValueError):
        module('backup_data').backup(src,destination)


def test_production_specs_use_independent_configured_paths(tmp_path):
    config={'projectRoot':str(tmp_path/'code'),'dataDirectory':str(tmp_path/'data'),
            'pythonExecutable':'python','nodeExecutable':'node','apiPort':18880,'webPort':18881,
            'environmentFile':str(tmp_path/'absent.json')}
    specs=module('run_server').launch_specs(config)
    assert specs[0][1][-1]=='--no-access-log'
    assert specs[1][3]['API_BASE_URL']=='http://127.0.0.1:18880'
    assert specs[1][3]['BAZI_DB_PATH']==str(tmp_path/'data/charts.sqlite')
    assert specs[1][3]['PORT']=='18881'
    assert specs[1][3]['HOSTNAME']=='127.0.0.1'


def test_production_config_rejects_public_bind(tmp_path):
    import json
    config={'projectRoot':str(tmp_path),'pythonExecutable':str(tmp_path/'python'),
            'nodeExecutable':str(tmp_path/'node'),'dataDirectory':str(tmp_path/'data'),
            'logDirectory':str(tmp_path/'logs'),'apiHost':'0.0.0.0','webHost':'127.0.0.1',
            'apiPort':18880,'webPort':18881}
    path=tmp_path/'server.json';path.write_text(json.dumps(config),encoding='utf8')
    with pytest.raises(ValueError,match='loopback'):
        module('run_server').load_config(path)


def test_magpie_credentials_only_reach_api_and_report_passes_restore(tmp_path,monkeypatch):
    import json
    from app.storage import ChartStore
    from app.access import PassStore
    monkeypatch.setenv('MAGPIE_API_KEY','inherited-secret')
    config={'projectRoot':str(tmp_path/'code'),'dataDirectory':str(tmp_path/'data'),
            'pythonExecutable':'python','nodeExecutable':'node','apiPort':18885,'webPort':18886,
            'magpieConfigFile':str(tmp_path/'magpie.json'),'publicOrigin':'https://ziping.example.com'}
    specs=module('run_server').launch_specs(config)
    assert specs[0][3]['MAGPIE_CONFIG_FILE']==config['magpieConfigFile']
    assert specs[0][3]['BAZI_PUBLIC_ORIGIN']=='https://ziping.example.com'
    assert not any(k.startswith(('MAGPIE_','OPENAI_')) for k in specs[1][3])
    source=tmp_path/'data/charts.sqlite'
    charts=ChartStore(source)
    charts.add({'id':'restored','locked':False})
    charts.freeze({'id':'restored','locked':True})
    passes=PassStore(source.with_suffix('.access.sqlite'))
    code=passes.issue();passes.redeem(code,'restored')
    destination=tmp_path/'backup/charts.sqlite'
    module('backup_data').backup_project(source,destination)
    assert PassStore(destination.with_suffix('.access.sqlite')).lookup(code)=='restored'
    assert ChartStore(destination).get('restored',True)['locked']


def test_reverse_tunnel_is_loopback_only_and_refuses_missing_identity(tmp_path):
    key=tmp_path/'ziping_ed25519';key.write_text('fixture')
    hosts=tmp_path/'known_hosts';hosts.write_text('fixture')
    config={'identityFile':str(key),'knownHostsFile':str(hosts),'sshPort':22,'remotePort':18890,
            'localPort':18886,'host':'example.org','username':'ziping'}
    cmd=module('run_tunnel').command(config)
    assert cmd[cmd.index('-R')+1]=='127.0.0.1:18890:127.0.0.1:18886'
    assert '-NT' in cmd and 'StrictHostKeyChecking=yes' in cmd and 'ExitOnForwardFailure=yes' in cmd
    config['identityFile']=str(tmp_path/'missing')
    with pytest.raises(ValueError):module('run_tunnel').command(config)
