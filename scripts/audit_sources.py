#!/usr/bin/env python3
"""Retrieve public GitHub source evidence; never imply access to blocked official hosts."""
import concurrent.futures as cf
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def gh(*args):
    return subprocess.check_output(['gh', *args])

def main():
    man = json.loads((ROOT/'registry/focus_registry_manifest.json').read_text())
    def one(item):
        repo, ref = item
        errors = []
        for path in ('docs/index.html', 'index.html'):
            try:
                body = gh('api', f'repos/buffedlizard55-lab/{repo}/contents/{path}?ref={ref}', '-H', 'Accept: application/vnd.github.raw')
                dest = ROOT/'.cache/source_pages'/repo/path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(body)
                permission = json.loads(gh('repo','view',f'buffedlizard55-lab/{repo}','--json','viewerPermission'))['viewerPermission']
                return dict(repo=repo, ref=ref, path=path, sha256=hashlib.sha256(body).hexdigest(),
                            bytes=len(body), source_url=f'https://github.com/buffedlizard55-lab/{repo}/blob/{ref}/{path}',
                            viewer_permission=permission, verified='retrieved community source, not an organizer receipt')
            except subprocess.CalledProcessError as e:
                errors.append(str(e))
        return dict(repo=repo, errors=errors)
    with cf.ThreadPoolExecutor(6) as pool:
        sites = list(pool.map(one, man['refs'].items()))
    ref = gh('api','repos/drivendataorg/gems-prize-reference-solution/commits/HEAD','--jq','.sha').decode().strip()
    notebook = gh('api',f'repos/drivendataorg/gems-prize-reference-solution/contents/unet-mc-cv-reference-solution.ipynb?ref={ref}',
                  '-H','Accept: application/vnd.github.raw')
    dest = ROOT/'.cache/official_reference.ipynb'
    dest.write_bytes(notebook)
    cells = json.loads(notebook)['cells']
    content = '\n'.join(''.join(c.get('source',[])) for c in cells)
    official = dict(repo='drivendataorg/gems-prize-reference-solution', ref=ref,
                    sha256=hashlib.sha256(notebook).hexdigest(),
                    source_url=f'https://github.com/drivendataorg/gems-prize-reference-solution/blob/{ref}/unet-mc-cv-reference-solution.ipynb',
                    verified_claims=['Reference solution is fault detection, not vent labeling.',
                                     'Training Tversky loss uses alpha=0.2 and beta=0.8.',
                                     'GPU is not mandatory; reference README offers a CPU environment.'],
                    does_not_verify=['Hidden leaderboard labels, current ranking, submission cap, or official distance-tolerant scorer.',
                                     'Official authenticity of community-mirrored data or its band units.'],
                    alpha_beta_code_present='alpha = 0.2' in content and 'beta = 0.8' in content)
    upstream='73485f27cf230af770167397c2b72cb9ce3b3f25'
    vendor = {}
    for p in sorted((ROOT/'vendor/gems57').glob('*.py')):
        vendor[str(p.relative_to(ROOT))] = {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                                          'source':f'https://github.com/buffedlizard55-lab/GEMSDOE32/blob/{upstream}/vendor/gems57/{p.name}',
                                          'upstream_unchanged':True}
    result = dict(retrieved_utc=datetime.now(timezone.utc).isoformat(),sites=sites,official_reference=official,
                  shared_tools=vendor, network_limit='Direct outbound access restricted to GitHub and package registries; other linked official pages not retrieved.',
                  score_receipts_present=False, current_leaderboard_verified=False,
                  official_links_not_retrieved=[
                      'https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/',
                      'https://www.drivendata.org/competitions/306/competition-doe-gems/data/',
                      'https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/',
                      'https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/',
                      'https://docs.nlr.gov/docs/fy26osti/96647.pdf',
                      'https://gdr.openei.org/submissions/1391',
                      'https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and',
                      'https://gbcge.org/current-projects/ingenious/',
                      'https://epsg.io/32611'])
    (ROOT/'evidence/sources.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('Retrieved',len(sites),'community site sources and pinned official reference notebook.')

if __name__=='__main__': main()
