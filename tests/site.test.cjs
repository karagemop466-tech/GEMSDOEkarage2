const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');

const root = path.join(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'docs/assets/app.js'), 'utf8');
const originalAudit = JSON.parse(fs.readFileSync(path.join(root, 'docs/data/focus_audit.json')));
const originalMonitor = JSON.parse(fs.readFileSync(path.join(root, 'docs/data/monitor.json')));

async function render(page, audit = originalAudit, monitor = originalMonitor, hash = '') {
  const html = fs.readFileSync(path.join(root, 'docs', page), 'utf8');
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(html, {url: `https://example.test/${page}${hash}`, runScripts: 'outside-only', virtualConsole});
  dom.window.fetch = async url => ({ok: true, json: async () => url.includes('focus_audit') ? audit : monitor});
  dom.window.eval(app);
  // The application only awaits two already-resolved fetch/json promises here.
  await new Promise(resolve => setImmediate(resolve));
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(errors, []);
  return dom;
}

test('dashboard renders nine research rows and keeps submission disabled', async () => {
  const dom = await render('index.html');
  const doc = dom.window.document;
  assert.equal(doc.querySelectorAll('#scorecard-body tr').length, 9);
  assert.equal(doc.querySelectorAll('.research-link').length, 9);
  assert.equal(doc.querySelector('.decision-card button').disabled, true);
  assert.match(doc.querySelector('#scorecard-body').textContent, /0\.2778/);
  assert.match(doc.querySelector('#scorecard-body').textContent, /USER-REPORTED/);
  assert.match(doc.querySelector('#scorecard-body').textContent, /DO NOT SUBMIT/);
  const research = doc.querySelector('#research-download');
  assert.match(research.textContent, /DO NOT SUBMIT/);
  assert.match(research.textContent, /HOLDOUT-DTI/);
  assert.equal(research.querySelectorAll('a[download]').length, 2);
  assert.match(research.querySelector('a[download]').getAttribute('href'), /DO-NOT-SUBMIT/);
  assert.doesNotMatch(research.textContent, /unique research TIF/i);
  for (const link of research.querySelectorAll('a[download]')) {
    assert.ok(fs.existsSync(path.join(root, 'docs', link.getAttribute('href'))));
  }
  dom.window.close();
});

test('site guide displays all nine detail cards even with a deep link', async () => {
  const dom = await render('executive-summary.html', originalAudit, originalMonitor, '#GEMSDOE32');
  assert.equal(dom.window.document.querySelectorAll('.site-detail').length, 9);
  assert.ok(dom.window.document.querySelector('#GEMSDOE32'));
  for (const link of dom.window.document.querySelectorAll('.site-detail a[href^="sites/"]')) {
    assert.ok(fs.existsSync(path.join(root, 'docs', link.getAttribute('href'))));
  }
  assert.equal(dom.window.document.querySelectorAll('.site-detail a[href^="sites/"]').length, 9);
  dom.window.close();
});

test('malformed score data fail closed rather than rendering zero', async () => {
  const altered = structuredClone(originalAudit);
  altered.sites[0].reported_score = null;
  const dom = await render('index.html', altered);
  const body = dom.window.document.querySelector('#scorecard-body');
  assert.match(body.textContent, /could not be loaded/i);
  assert.equal(body.querySelectorAll('.research-link').length, 0);
  dom.window.close();
});

test('rendered filenames are text, not executable HTML', async () => {
  const altered = structuredClone(originalAudit);
  altered.sites[0].filename = '<img src=x onerror=alert(1)>';
  const dom = await render('index.html', altered);
  const file = dom.window.document.querySelector('#scorecard-body .file-name');
  assert.equal(file.textContent, '<img src=x onerror=alert(1)>');
  assert.equal(file.querySelector('img'), null);
  dom.window.close();
});

test('a failed leaderboard refresh remains visibly stale while source status is shown', async () => {
  const m = structuredClone(originalMonitor);
  m.leaderboard = {status: 'unavailable', last_successful: {score_text: '0.4544', checked_utc: '2026-10-27T20:58:21Z'}};
  const dom = await render('index.html', originalAudit, m);
  const doc = dom.window.document;
  assert.equal(doc.querySelector('#leaderboard-score').textContent, '0.4544');
  assert.match(doc.querySelector('#leaderboard-status').textContent, /STALE/);
  assert.match(doc.querySelector('#table-note').textContent, /Source-head check/);
  dom.window.close();
});

test('dashboard table headers match every rendered row', async () => {
  for (const page of ['index.html', 'executive-summary.html']) {
    const dom = await render(page);
    const doc = dom.window.document;
    const headers = doc.querySelectorAll('.scorecard thead th').length;
    assert.equal(headers, 5);
    for (const row of doc.querySelectorAll('#scorecard-body tr')) {
      assert.equal(row.children.length, headers);
    }
    assert.doesNotMatch(doc.body.textContent, /labels\.tif requires DrivenData login/);
    assert.match(doc.body.textContent, /negative|failed/);
    assert.ok(doc.querySelector('a[href="experiment-executive-summary.html"]'));
    dom.window.close();
  }
});

test('current download does not claim established uniqueness or submission readiness', async () => {
  const dom = await render('index.html');
  const text = dom.window.document.querySelector('#research-download').textContent;
  assert.match(text, /uniqueness not established/);
  assert.match(text, /DO NOT SUBMIT/);
  assert.doesNotMatch(text, /unique research TIF|\(submission raster\)/);
  dom.window.close();
});

test('K2 literal-policy review is negative and links only to a research artifact', async () => {
  const home = await render('index.html');
  const section = home.window.document.querySelector('#k2-candidate');
  assert.match(section.textContent, /research artifact/i);
  assert.match(section.textContent, /DO NOT SUBMIT/);
  assert.match(section.textContent, /SELECTOR NEGATIVE|No slot is approved/);
  assert.match(section.querySelector('a[download]').textContent, /DO NOT SUBMIT/);
  assert.match(section.innerHTML, /evidence\/k2-review-2026-10-28\.json/);
  home.window.close();

  const summary = await render('executive-summary.html');
  const k2 = summary.window.document.querySelector('#k2');
  assert.match(k2.textContent, /negative/i);
  assert.match(k2.textContent, /DO NOT SUBMIT/);
  assert.match(k2.querySelector('thead').textContent, /File for research/);
  summary.window.close();
});
