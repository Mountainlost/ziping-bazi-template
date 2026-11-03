"""Export the existing Next.js frontend with a synthetic report for GitHub Pages."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ID = '00000000-0000-4000-8000-000000000001'


def edit(root, file, old, new):
    path = root / 'src' / file
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise ValueError(f'Preview adapter no longer matches {file}')
    path.write_text(source.replace(old, new), encoding='utf-8')


def export_frontend(output, base):
    if not re.fullmatch(r'(?:/[A-Za-z0-9._-]+)*', base):
        raise ValueError('Use a GitHub Pages base path such as /repository-name')
    if output.exists():
        raise FileExistsError(output)

    sys.path.insert(0, str(ROOT / 'apps/api'))
    from app.locations import location_index
    from app.models import BirthInput
    from app.services.bazi.chart import generate_candidates
    from app.services.report.chart_image import render_chart_svg
    from app.services.report.renderer import render
    from app.services.rules.engine import analyze

    birth = BirthInput(calendar='solar', year=2000, month=5, day=20, time='10:15',
                       accuracy='exact', sex='女', name='示例命盘', province='北京市',
                       city='北京市', district='东城区', longitude=116.4,
                       latitude=39.9, referenceYear=2026)
    chart = analyze(generate_candidates(birth)[0])
    chart.update(id=SAMPLE_ID, report=render(chart), locked=True)

    with TemporaryDirectory(prefix='ziping-pages-') as temporary:
        web = Path(temporary) / 'web'
        shutil.copytree(ROOT / 'apps/web', web, ignore=shutil.ignore_patterns(
            'node_modules', '.next', 'out', '*.tsbuildinfo', '.env*', 'api', 'favicon.ico'))
        (web / 'next.config.ts').write_text(
            f"export default {{output:'export', basePath:{json.dumps(base)}, "
            "trailingSlash:true, devIndicators:false, images:{unoptimized:true}};\n",
            encoding='utf-8')
        edit(web, 'app/[stage]/page.tsx', 'export default async function StagePage',
             "export function generateStaticParams() {\n"
             "  return ['verify','overview','analysis','cycles','conclusion'].map(stage => ({stage}));\n"
             "}\nexport default async function StagePage")

        # Read only exported fixtures. Never send data entered in the form.
        edit(web, 'lib/types.ts', '  const result = await fetch(', f"""
  if (body !== undefined) throw new Error('当前为 GitHub Pages 预览。请部署完整项目后排盘或提问。');
  if (url === '/status') return {{ aiConfigured: false }} as T;
  if (url.endsWith('/access')) return {{ authorized: false, remaining: 0, history: [] }} as T;
  const files: Record<string, string> = {{
    '/locations': 'locations.json',
    '/charts/{SAMPLE_ID}': 'chart.json',
  }};
  const file = files[url];
  if (!file) throw new Error('这份报告不在静态预览中。');
  const result = await fetch(""")
        edit(web, 'lib/types.ts', '`/api/v1${url}`', f'`{base}/preview/${{file}}`')
        edit(web, 'components/session.tsx', "    const id = sessionStorage.getItem('ziping-current');",
             f"""    if (new URLSearchParams(window.location.search).has('demo')) {{
      sessionStorage.setItem('ziping-current', '{SAMPLE_ID}');
      sessionStorage.removeItem('ziping-candidates');
    }}
    const id = sessionStorage.getItem('ziping-current');""")
        banner = (f'<aside aria-label="预览说明" style={{{{background:"#edf2ff",color:"#1b315c",'
                  'padding:"10px 24px",fontSize:"14px",textAlign:"center"}}>'
                  'GitHub Pages 预览 · 排盘和大师问答需自行部署。'
                  f' <a href="{base}/overview/?demo=1" style={{{{textDecoration:"underline"}}}}>查看完整示例报告</a>'
                  '</aside>')
        edit(web, 'app/layout.tsx', '<SessionProvider>{children}', banner + '<SessionProvider>{children}')
        for file in ('master-content', 'master-chat'):
            edit(web, f'components/{file}.tsx', 'src="/images/', f'src="{base}/images/')
        edit(web, 'components/chart-attachment.tsx', '{`/api/v1/charts/${chart.id}/image.svg`}',
             f'"{base}/preview/chart.svg"')

        fixtures = web / 'public/preview'
        fixtures.mkdir(parents=True)
        (fixtures / 'locations.json').write_text(json.dumps(location_index(), ensure_ascii=False), encoding='utf-8')
        (fixtures / 'chart.json').write_text(json.dumps(chart, ensure_ascii=False), encoding='utf-8')
        (fixtures / 'chart.svg').write_text(render_chart_svg(chart), encoding='utf-8')

        npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
        if not npm:
            raise RuntimeError('npm is required')
        subprocess.run([npm, 'ci', '--no-audit', '--no-fund'], cwd=web, check=True)
        subprocess.run([npm, 'run', 'build'], cwd=web, check=True)
        shutil.copytree(web / 'out', output)
        (output / '.nojekyll').touch()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--base-path', default='')
    options = parser.parse_args()
    export_frontend(options.output.resolve(), options.base_path)
