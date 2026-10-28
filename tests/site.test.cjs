const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {JSDOM, VirtualConsole} = require('jsdom');

const root = path.join(__dirname, '..');
const homePath = path.join(root, 'docs/experiment-index.html');
const home = fs.readFileSync(homePath, 'utf8');
const siteScript = fs.readFileSync(path.join(root, 'docs/assets/site.js'), 'utf8');
const runCard = JSON.parse(fs.readFileSync(path.join(root, 'evidence/run_card.json')));

function parse(html, url = 'https://example.test/docs/experiment-index.html') {
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(html, {url, runScripts: 'outside-only', virtualConsole});
  return {dom, errors};
}

test('canonical executive summary has nine historical rows and a locked release', () => {
  const {dom, errors} = parse(home);
  const doc = dom.window.document;
  const rows = [...doc.querySelectorAll('.table-wrap tbody tr')];
  assert.equal(rows.length, 9);
  assert.match(doc.body.textContent, /0\.2778[\s\S]*?Unverified user report/);
  assert.equal(doc.querySelectorAll('button[disabled]').length, 1);
  assert.match(doc.querySelector('button[disabled]').textContent, /No approved submission TIF/);
  assert.match(doc.querySelector('#downloads').textContent, /DO NOT SUBMIT/);
  const links = [...doc.querySelectorAll('#downloads a[download]')];
  assert.equal(links.length, 2);
  for (const link of links) {
    const relative = link.getAttribute('href');
    assert.match(relative, /DO-NOT-SUBMIT/);
    assert.ok(fs.existsSync(path.join(root, 'docs', relative)));
  }
  assert.equal(errors.length, 0);
  dom.window.close();
});

test('research download bytes match the negative run card, never an approval receipt', () => {
  const file = path.join(root, runCard.raster);
  const bytes = fs.readFileSync(file);
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), runCard.raster_sha256);
  assert.equal(runCard.verdict, 'negative');
  assert.equal(runCard.approved_for_weekly_slot, false);
  assert.equal(runCard.unique_submission_verified, false);
});

test('submission guide contains no current downloadable file and clearly blocks upload', () => {
  const guide = fs.readFileSync(path.join(root, 'docs/submission-guide.html'), 'utf8');
  assert.match(guide, /CURRENT RELEASE: DO NOT SUBMIT/);
  assert.match(guide, /No file is currently promoted/);
  assert.match(guide, /this release.s TIF is a research surface only/i);
  assert.equal((guide.match(/download="[^"]*\.tif/gi) || []).length, 0);
});

test('source refresh renders changed revisions as stale and never grants clearance', async () => {
  const {dom} = parse(home);
  const window = dom.window;
  const data = JSON.parse(fs.readFileSync(path.join(root, 'docs/evidence/freshness.json')));
  const changedRepo = Object.keys(data.refs)[0];
  window.fetch = async url => {
    if (url === 'evidence/freshness.json') return {ok:true, json:async () => data};
    const repo = decodeURIComponent(String(url).match(/repos\/buffedlizard55-lab\/([^/]+)\/commits/)[1]);
    return {ok:true, json:async () => ({sha:repo === changedRepo ? 'f'.repeat(40) : data.refs[repo]})};
  };
  window.eval(siteScript);
  await window.document.getElementById('refresh-sources').click();
  await new Promise(resolve => setImmediate(resolve));
  await new Promise(resolve => setImmediate(resolve));
  const text = window.document.getElementById('freshness-results').textContent;
  assert.match(text, /NEW REVISION/);
  assert.match(text, /no automatic clearance/);
  assert.equal(window.document.getElementById('refresh-sources').disabled, false);
  dom.window.close();
});

test('source refresh fails closed when network is unavailable', async () => {
  const {dom} = parse(home);
  const window = dom.window;
  window.fetch = async () => { throw new Error('offline'); };
  window.eval(siteScript);
  await window.document.getElementById('refresh-sources').click();
  await new Promise(resolve => setImmediate(resolve));
  assert.match(window.document.getElementById('freshness-status').textContent, /Freshness not verified/);
  assert.equal(window.document.getElementById('refresh-sources').disabled, false);
  dom.window.close();
});
