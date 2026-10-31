const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');

const root = path.join(__dirname, '..');
const card = JSON.parse(fs.readFileSync(path.join(root, 'evidence/hk3/run_card.json')));
const witness = JSON.parse(fs.readFileSync(path.join(root, 'evidence/hk3/literal_recheck.json')));
const pages = ['index.html', 'executive-summary.html', 'how-to-submit.html', 'submit.html'];

function render(page) {
  const html = fs.readFileSync(path.join(root, 'docs', page), 'utf8');
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(html, {url: `https://example.test/docs/${page}`, runScripts: 'outside-only', virtualConsole});
  assert.deepEqual(errors, []);
  return dom;
}

test('desk pages carry the release badge and keep their historical negative verdicts', () => {
  // The HK3 card (a retired research file) stays negative. The header badge is now
  // driven by evidence/halo/final_generation.json, because one file passed every
  // gate on 2026-10-31; each desk page keeps its own historical audit verdicts.
  assert.equal(card.verdict, 'negative');
  assert.equal(witness.duplicate_stop, true);
  const release = JSON.parse(fs.readFileSync(path.join(root, 'evidence/halo/final_generation.json')));
  const strictPass = release.verdict.ok_to_submit && release.uniqueness_literal_gate.unique === true;
  const expected = strictPass ? 'OK TO SUBMIT: 1 FILE · SEE RELEASE' : 'NO FILE CLEARED · DO NOT SUBMIT';
  for (const page of pages) {
    const dom = render(page);
    const badge = dom.window.document.querySelector('.header .badge');
    assert.equal(badge.textContent, expected);
    assert.ok(badge.classList.contains(strictPass ? 'ok' : 'no'));
    assert.match(dom.window.document.body.textContent, /DO NOT SUBMIT/);
    dom.window.close();
  }
});

test('the release decision page is the live decision and its download is the released file', () => {
  const dom = render('release.html');
  const doc = dom.window.document;
  const badge = doc.querySelector('.header .badge');
  const release = JSON.parse(fs.readFileSync(path.join(root, 'evidence/halo/final_generation.json')));
  assert.equal(badge.textContent, release.verdict.ok_to_submit && release.uniqueness_literal_gate.unique === true
    ? 'OK TO SUBMIT: YES · 1 FILE' : 'NO FILE CLEARED · DO NOT SUBMIT');
  assert.match(doc.body.textContent, /NO FILE CLEARED UNDER THE LITERAL UNIQUENESS RULE/);
  const links = [...doc.querySelectorAll('a[download]')];
  assert.ok(links.length >= 1, 'at least one one-click download');
  for (const link of links) {
    assert.equal(link.getAttribute('href'), `downloads/${release.submission_file.split('/').pop()}`);
    assert.ok(fs.existsSync(path.join(root, 'docs', link.getAttribute('href'))));
  }
  assert.ok(doc.body.textContent.includes(release.format_checks.sha256));
  const rows = doc.querySelectorAll('#release-table tbody tr');
  assert.equal(rows.length, 10, 'nine focus sites plus the released file');
  dom.window.close();
});

test('root landing page fails closed on the conflicting HALO and GBM release records', () => {
  const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const dom = new JSDOM(html, {url: 'https://example.test/', runScripts: 'outside-only'});
  const doc = dom.window.document;
  const text = doc.body.textContent;
  assert.match(text, /NO SINGLE SUBMISSION SELECTED/);
  assert.match(text, /selector conflict/);
  assert.match(text, /Both therefore fail the literal stop/);
  assert.match(text, /99\.84%/);
  assert.match(text, /93\.77%/);
  assert.match(text, /slot_authorized/);
  assert.ok([...doc.querySelectorAll('a[href]')].some(a => a.getAttribute('href') === 'docs/release.html'));
  assert.ok([...doc.querySelectorAll('a[href]')].some(a => a.getAttribute('href') === 'docs/release-summary.html'));
  assert.equal(doc.querySelectorAll('a[download]').length, 0, 'landing page must not silently select a candidate');
  assert.equal(doc.querySelector('meta[http-equiv="refresh"]'), null, 'no automatic redirect past the warning');
  assert.doesNotMatch(html, /prediction|score\s*=\s*0\.\d+/i, 'no unlabeled score projection on landing page');
  dom.window.close();
});

test('one-click research download is visibly labeled and the exact bytes exist', () => {
  const k10 = JSON.parse(fs.readFileSync(path.join(root, 'evidence/k10/run_card.json'), 'utf8'));
  const s1 = JSON.parse(fs.readFileSync(path.join(root, 'evidence/s1/run_card.json'), 'utf8'));
  const candidateName = path.basename(k10.raster);
  const s1Name = path.basename(s1.raster.file);
  const habitat = JSON.parse(fs.readFileSync(path.join(root, 'evidence/run-card-gemsdoekarage2-geo-habitat-dti-20261031.json'), 'utf8'));
  const habitatName = path.basename(habitat.file.path);
  const halo = JSON.parse(fs.readFileSync(path.join(root, 'evidence/halo/final_generation.json'), 'utf8'));
  const haloName = path.basename(halo.submission_file);
  const gbm = JSON.parse(fs.readFileSync(path.join(root, 'docs/downloads/gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.run-card.json'), 'utf8'));
  const gbmName = path.basename(gbm.file);
  const currentArtifacts = new Set([candidateName, s1Name, habitatName, haloName, gbmName]);
  for (const page of pages) {
    const dom = render(page);
    const links = [...dom.window.document.querySelectorAll('a[download]')];
    const research = links.filter(l => /gemsdoekarage2-hk3-edgecentrality/.test(l.getAttribute('href')));
    // Exactly one click-to-download RESEARCH ONLY link (the HK3 file), plus at
    // most the selector-cleared candidate link (submission desk points there).
    assert.ok(research.length >= 1, `${page}: research link`);
    for (const link of research) {
      assert.match(link.textContent, /RESEARCH ONLY/);
      assert.match(link.getAttribute('href'), /gemsdoekarage2-hk3-edgecentrality/);
      assert.ok(fs.existsSync(path.join(root, 'docs', link.getAttribute('href'))));
      assert.match(link.closest('section').textContent, /DO NOT SUBMIT/);
    }
    for (const link of links) {
      const href = path.basename(link.getAttribute('href'));
      assert.ok(
        /gemsdoekarage2-hk3-edgecentrality/.test(href) || currentArtifacts.has(href),
        `${page}: unexpected download link ${href}`);
      assert.ok(fs.existsSync(path.join(root, 'docs', link.getAttribute('href'))), `${page}: missing download bytes ${href}`);
    }
    dom.window.close();
  }
});

test('homepage shows the exact witness and no candidate leaderboard projection', () => {
  const dom = render('index.html');
  const text = dom.window.document.body.textContent;
  assert.ok(text.includes(card.raster.sha256));
  assert.match(text, /HOLDOUT-DTI/);
  assert.match(text, /45,046 of 45,108 dots \(99\.86%\)/);
  assert.match(text, /Leaderboard estimate\s*Unavailable/);
  assert.match(text, /not a leaderboard estimate/i);
  assert.match(text, /uncertified|unauthenticated/i);
  assert.doesNotMatch(text, /Literal-rule exception applied:\s*yes/i);
  assert.doesNotMatch(text, /0\.263\s*[–-]\s*0\.286/);
  dom.window.close();
});

test('current public snapshot corrects the user-cited rank and keeps research status separate', () => {
  const dom = render('index.html');
  const text = dom.window.document.body.textContent;
  assert.match(text, /2026-10-30/);
  assert.match(text, /xiaofanhu: 0\.4544 at rank 1/);
  assert.match(text, /0\.3195 appeared at rank 48 for kpomazi/);
  assert.match(text, /not file-linked submission receipts, private-round results/);
  assert.match(text, /GITHUB METADATA ONLY/);
  assert.match(text, /No latest-head raster\/score audit is claimed/);
  assert.ok([...dom.window.document.querySelectorAll('a[href]')].some(a => a.getAttribute('href') === 'evidence/official-review-2026-10-30.json'));
  dom.window.close();
});

test('nine-site table links pinned historical files and labels values unverified', () => {
  const dom = render('index.html');
  const rows = [...dom.window.document.querySelectorAll('#nine-sites tbody tr')];
  assert.equal(rows.length, 9);
  const text = rows.map(r => r.textContent).join('\n');
  assert.match(text, /0\.2778/);
  for (const site of ['GEMSDOE24', 'GEMSDOE25', 'GEMSDOE27', 'GEMSDOE28', 'GEMSDOE30', 'GEMSDOE31', 'GEMSDOE32', 'GEMSDOE33', 'GEMSDOE36']) {
    assert.match(text, new RegExp(site));
  }
  for (const row of rows) {
    assert.equal(row.children.length, 6);
    assert.match(row.textContent, /USER-REPORTED\s*\/\s*UNVERIFIED/);
    assert.match(row.textContent, /DO NOT SUBMIT/);
    assert.match(row.textContent, /PROJECTION for .*a model, not a score/);
    assert.ok([...row.querySelectorAll('a')].some(a => a.href.includes('/raw/')));
  }
  dom.window.close();
});

test('legacy artefacts stay quarantined with their receipts', () => {
  for (const page of pages) {
    const dom = render(page);
    const legacy = dom.window.document.querySelector('#legacy');
    assert.ok(legacy, `${page}: legacy section missing`);
    assert.match(legacy.textContent, /DO NOT SUBMIT/);
    assert.match(legacy.textContent, /prior literal-policy verdict for K2: NEGATIVE/);
    assert.match(legacy.textContent, /not unique/);
    assert.equal(legacy.querySelectorAll('a[download]').length, 0);
    assert.match(legacy.innerHTML, /evidence\/k2-review-2026-10-28\.json/);
    dom.window.close();
  }
});

test('every relative link on the desk pages resolves to a published file', () => {
  for (const page of pages) {
    const dom = render(page);
    for (const a of dom.window.document.querySelectorAll('a[href]')) {
      const href = a.getAttribute('href');
      if (/^(https?:|mailto:|#)/.test(href)) continue;
      const target = href.split('#')[0];
      assert.ok(fs.existsSync(path.join(root, 'docs', target)), `${page}: ${href}`);
    }
    dom.window.close();
  }
});

test('official sources and complete holdout labels are linked on the summary', () => {
  const dom = render('executive-summary.html');
  const hrefs = [...dom.window.document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  assert.ok(hrefs.includes('https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/'));
  assert.ok(hrefs.includes('https://github.com/drivendataorg/gems-prize-reference-solution'));
  assert.match(dom.window.document.body.textContent, /gems57-pooled-hide-v2/);
  assert.match(dom.window.document.body.textContent, /58,258 withheld positives/);
  assert.match(dom.window.document.body.textContent, /95% CI/);
  dom.window.close();
});
