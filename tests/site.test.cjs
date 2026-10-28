const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');

const root = path.join(__dirname, '..');
const card = JSON.parse(fs.readFileSync(path.join(root, 'evidence/hk3/run_card.json')));
const approved = false; // current hard-stop policy rejects the historical PROMOTE card

function render(page) {
  const html = fs.readFileSync(path.join(root, 'docs', page), 'utf8');
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(html, {url: `https://example.test/docs/${page}`, runScripts: 'outside-only', virtualConsole});
  assert.deepEqual(errors, []);
  return dom;
}

const pages = ['index.html', 'executive-summary.html', 'how-to-submit.html', 'submit.html'];

test('every desk page carries the fail-closed current status and no unresolved placeholder', () => {
  for (const page of pages) {
    const dom = render(page);
    const badge = dom.window.document.querySelector('.header .badge');
    assert.ok(badge, `${page}: badge missing`);
    assert.equal(badge.textContent, approved ? 'OK TO SUBMIT: YES' : 'NO APPROVED SUBMISSION');
    assert.ok(badge.classList.contains(approved ? 'ok' : 'no'));
    assert.match(dom.window.document.body.textContent, /DO NOT SUBMIT/);
    assert.doesNotMatch(dom.window.document.body.innerHTML, /\{BADGE/);
    dom.window.close();
  }
});

test('the only click-to-download links are the file named by the run card, and the bytes exist', () => {
  for (const page of pages) {
    const dom = render(page);
    const links = [...dom.window.document.querySelectorAll('a[download]')];
    if (page === 'index.html' || page === 'how-to-submit.html') assert.ok(links.length >= 1, `${page}: no download link`);
    for (const link of links) {
      const href = link.getAttribute('href');
      assert.match(href, new RegExp(card.submission.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
      assert.doesNotMatch(href, /k2-hgbcont|h1-parity|hkarage1|DO-NOT-SUBMIT/);
      assert.ok(fs.existsSync(path.join(root, 'docs', href)), `${page}: ${href} missing`);
    }
    dom.window.close();
  }
});

test('homepage: SHA-256, labelled estimate, holdout label, uniqueness tiers and the literal failures are visible', () => {
  const dom = render('index.html');
  const text = dom.window.document.body.textContent;
  assert.match(text, new RegExp(card.raster.sha256));
  assert.match(text, /HOLDOUT-DTI/);
  assert.match(text, /LEADERBOARD-CALIBRATED ESTIMATE/);
  assert.match(text, /NOT ORGANIZER-CONFIRMED/);
  assert.match(text, /Literal 70 % rule vs all 450 non-degenerate registry rasters:\s*FAIL/);
  const failures = card.registry_uniqueness.tiers.U2_literal_rule_vs_all_registry_rasters.failures;
  assert.ok(failures.length >= 1);
  for (const row of failures) {
    assert.match(text, new RegExp(path.basename(row.submission).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
  // gate list mirrors the card: every gate key has a PASS/FAIL row
  const booleanGates = Object.entries(card.gates).filter(([k, v]) => typeof v === 'boolean' && k !== 'literal_rule_exception_applied');
  const gateRows = [...dom.window.document.querySelectorAll('.gates li')];
  assert.equal(gateRows.length, booleanGates.length + 4); // lane, pre-placement, runtime budget, and input provenance receipts are required
  const fails = gateRows.filter(li => li.querySelector('.pill.no'));
  assert.equal(fails.length, booleanGates.filter(([, v]) => v === false).length);
  assert.match(text, /Literal-rule exception applied:\s*yes/);
  assert.match(text, /NO APPROVED SUBMISSION/);
  assert.match(text, /RESEARCH ONLY — DO NOT SUBMIT/);
  dom.window.close();
});

test('homepage nine-site table lists all focus sites with user-reported scores and uniqueness verdicts', () => {
  const dom = render('index.html');
  const rows = [...dom.window.document.querySelectorAll('#nine-sites tbody tr')];
  assert.equal(rows.length, 9);
  const text = rows.map(r => r.textContent).join('\n');
  assert.match(text, /0\.2778/);
  assert.match(text, /USER-REPORTED/);
  for (const site of ['GEMSDOE24', 'GEMSDOE25', 'GEMSDOE27', 'GEMSDOE28', 'GEMSDOE30', 'GEMSDOE31', 'GEMSDOE32', 'GEMSDOE33', 'GEMSDOE36']) {
    assert.match(text, new RegExp(site));
  }
  for (const row of rows) assert.equal(row.children.length, dom.window.document.querySelectorAll('#nine-sites thead th').length);
  dom.window.close();
});

test('legacy artefacts stay quarantined with their receipts', () => {
  for (const page of ['index.html', 'executive-summary.html', 'how-to-submit.html']) {
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

test('official sources are linked with the competition metric page', () => {
  const dom = render('executive-summary.html');
  const hrefs = [...dom.window.document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  assert.ok(hrefs.includes('https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/'));
  assert.ok(hrefs.includes('https://github.com/drivendataorg/gems-prize-reference-solution'));
  dom.window.close();
});
