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

test('all desk pages are fail-closed and visibly prohibit submission', () => {
  assert.equal(card.verdict, 'negative');
  assert.equal(witness.duplicate_stop, true);
  for (const page of pages) {
    const dom = render(page);
    const badge = dom.window.document.querySelector('.header .badge');
    assert.equal(badge.textContent, 'OK TO SUBMIT: NO');
    assert.ok(badge.classList.contains('no'));
    assert.match(dom.window.document.body.textContent, /DO NOT SUBMIT/);
    assert.doesNotMatch(dom.window.document.body.textContent, /OK TO SUBMIT:\s*YES/);
    dom.window.close();
  }
});

test('one-click research download is visibly labeled and the exact bytes exist', () => {
  for (const page of pages) {
    const dom = render(page);
    const links = [...dom.window.document.querySelectorAll('a[download]')];
    assert.equal(links.length, 1, `${page}: research link`);
    const link = links[0];
    assert.match(link.textContent, /RESEARCH ONLY/);
    assert.match(link.getAttribute('href'), /gemsdoekarage2-hk3-edgecentrality/);
    assert.ok(fs.existsSync(path.join(root, 'docs', link.getAttribute('href'))));
    assert.match(link.closest('section').textContent, /DO NOT SUBMIT/);
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
    assert.match(row.textContent, /Unavailable/);
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

test('research hypotheses name layers and controls without promising an unvalidated TIFF', () => {
  const dom = render('executive-summary.html');
  const text = dom.window.document.body.textContent;
  assert.match(text, /Next research slate · not tested or assigned/);
  for (const band of ['13', '11', '12', '19', '17', '18', '7', '8', '2', '3', '10', '16']) {
    assert.match(text, new RegExp(`Bands?[^\\n]*\\b${band}\\b`));
  }
  assert.match(text, /shoreline\/contour null/);
  assert.match(text, /saline groundwater\/playa margins/i);
  assert.match(text, /shuffled[- ]strain/i);
  assert.match(text, /shuffle seismicity as a negative control/i);
  assert.match(text, /organizer data tab is login-gated/);
  assert.match(text, /none is assigned or validated/i);
  assert.doesNotMatch(text, /New unique submission TIF — ready to download/);
  dom.window.close();
});
