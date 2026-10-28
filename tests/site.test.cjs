const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');

const root = path.join(__dirname, '..');
const card = JSON.parse(fs.readFileSync(path.join(root, 'evidence/hk3/strict_disposition.json')));
const historical = JSON.parse(fs.readFileSync(path.join(root, 'evidence/hk3/run_card.json')));
const selector = JSON.parse(fs.readFileSync(path.join(root, 'evidence/hk3/strict_selector_result.json')));
const ok = card.verdict === 'PROMOTE';

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

test('every desk page carries the current strict-disposition badge and no unresolved placeholder', () => {
  for (const page of pages) {
    const dom = render(page);
    const badge = dom.window.document.querySelector('.header .badge');
    assert.ok(badge, `${page}: badge missing`);
    assert.equal(badge.textContent, 'OK TO SUBMIT: NO');
    assert.ok(badge.classList.contains('no'));
    assert.doesNotMatch(dom.window.document.body.innerHTML, /\{BADGE/);
    assert.doesNotMatch(dom.window.document.body.textContent, /OK TO SUBMIT: YES/);
    dom.window.close();
  }
});

test('download links are explicitly research-only and point only to the preserved HK3 bytes', () => {
  for (const page of pages) {
    const dom = render(page);
    const links = [...dom.window.document.querySelectorAll('a[download]')];
    assert.ok(links.length >= 1, `${page}: research download link missing`);
    for (const link of links) {
      const href = link.getAttribute('href');
      assert.match(href, new RegExp(card.submission.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
      assert.doesNotMatch(href, /k2-hgbcont|h1-parity|hkarage1|DO-NOT-SUBMIT/);
      assert.ok(fs.existsSync(path.join(root, 'docs', href)), `${page}: ${href} missing`);
      assert.match(link.textContent, /research|RESEARCH|DO NOT SUBMIT|ZIP/i);
    }
    dom.window.close();
  }
});

test('homepage surfaces strict duplicate, incomplete registry and exterior stops while preserving historical PROMOTE evidence', () => {
  const dom = render('index.html');
  const text = dom.window.document.body.textContent;
  assert.match(text, new RegExp(card.raster.sha256));
  assert.match(text, /DO NOT SUBMIT/);
  assert.match(text, /RESEARCH ONLY/);
  assert.match(text, /HOLDOUT-DTI/);
  assert.match(text, /LEADERBOARD-CALIBRATED ESTIMATE/);
  assert.match(text, /ORGANIZER-CONFIRMED/);
  assert.match(text, /99\.9%/);
  assert.match(text, /r13 spacing-5 lattice/);
  assert.match(text, /no exception/i);
  assert.match(text, /452 of 453/);
  assert.match(text, /outside_is_nan: false/);
  assert.match(text, /strict_format_pass: false/);
  assert.match(text, /Literal-rule exception applied: no/);
  assert.match(text, /historically says PROMOTE/);
  assert.equal(historical.verdict, 'PROMOTE');
  assert.equal(selector.verdict, 'negative');
  assert.equal(selector.ok_to_submit, false);

  const failures = card.registry_uniqueness.tiers.U2_literal_rule_vs_all_registry_rasters.failures;
  assert.equal(failures.length, 5);
  for (const row of failures) {
    assert.match(text, new RegExp(path.basename(row.submission).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    assert.match(text, new RegExp(`${(100 * row.overlap_3px).toFixed(1)}%`));
  }
  const booleanGates = Object.entries(card.gates).filter(([k, v]) => typeof v === 'boolean' && k !== 'literal_rule_exception_applied');
  const gateRows = [...dom.window.document.querySelectorAll('.gates li')];
  assert.equal(gateRows.length, booleanGates.length);
  const fails = gateRows.filter(li => li.querySelector('.pill.no'));
  assert.equal(fails.length, booleanGates.filter(([, v]) => v === false).length);
  dom.window.close();
});

test('homepage nine-site table lists all user-reported values and measured mask notes', () => {
  const dom = render('index.html');
  const rows = [...dom.window.document.querySelectorAll('#nine-sites tbody tr')];
  assert.equal(rows.length, 9);
  const text = rows.map(r => r.textContent).join('\n');
  assert.match(text, /0\.2778/);
  assert.match(text, /USER-REPORTED \/ UNVERIFIED/);
  for (const site of ['GEMSDOE24', 'GEMSDOE25', 'GEMSDOE27', 'GEMSDOE28', 'GEMSDOE30', 'GEMSDOE31', 'GEMSDOE32', 'GEMSDOE33', 'GEMSDOE36']) {
    assert.match(text, new RegExp(site));
  }
  for (const row of rows) assert.equal(row.children.length, dom.window.document.querySelectorAll('#nine-sites thead th').length);
  dom.window.close();
});

test('executive summary explains GEMSDOE32 cautiously and lists four unassigned hypotheses', () => {
  const dom = render('executive-summary.html');
  const text = dom.window.document.body.textContent;
  assert.match(text, /may explain GEMSDOE32/);
  assert.match(text, /plausible mechanism/);
  assert.match(text, /not established as the cause/);
  assert.match(text, /fault structures indicative of geothermal resources/);
  for (const hypothesis of ['Topography-conditioned residual gravity step', 'Conductivity saddle', 'Strain-regime change', 'Seismicity-sidedness']) {
    assert.match(text, new RegExp(hypothesis));
  }
  assert.match(text, /not implemented/);
  dom.window.close();
});

test('submission-status page has no upload directions for the rejected file', () => {
  const dom = render('how-to-submit.html');
  const text = dom.window.document.body.textContent;
  assert.match(text, /There are no upload instructions/);
  assert.match(text, /No weekly slot has been used or authorized/);
  assert.doesNotMatch(text, /Sign in to DrivenData/);
  assert.doesNotMatch(text, /Upload the TIF as the prediction file/);
  dom.window.close();
});

test('legacy research artefacts stay quarantined with their receipts', () => {
  for (const page of ['index.html', 'executive-summary.html', 'how-to-submit.html']) {
    const dom = render(page);
    const legacy = dom.window.document.querySelector('#legacy');
    assert.ok(legacy, `${page}: legacy section missing`);
    assert.match(legacy.textContent, /DO NOT SUBMIT/);
    assert.match(legacy.textContent, /prior literal-policy verdict for K2: NEGATIVE/);
    assert.match(legacy.textContent, /not unique/);
    assert.match(legacy.textContent, /No file is currently offered for upload/);
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

test('official sources and public leaderboard observation are linked with correct scope', () => {
  const dom = render('executive-summary.html');
  const hrefs = [...dom.window.document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  assert.ok(hrefs.includes('https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/'));
  assert.ok(hrefs.includes('https://github.com/drivendataorg/gems-prize-reference-solution'));
  const text = dom.window.document.body.textContent;
  assert.match(text, /not a submission receipt/);
  assert.match(text, /not a score for HK3/);
  dom.window.close();
});
