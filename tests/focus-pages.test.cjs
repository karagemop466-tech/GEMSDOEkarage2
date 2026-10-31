const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM} = require('jsdom');

const root = path.join(__dirname, '..');
const docs = path.join(root, 'docs');
const focusSites = JSON.parse(fs.readFileSync(path.join(root, 'registry/focus_sites.json'), 'utf8')).sites;
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'registry/focus_registry_manifest.json'), 'utf8')).rasters;
const geometry = JSON.parse(fs.readFileSync(path.join(root, 'evidence/geometry-audit.json'), 'utf8'));
const expectedSites = ['GEMSDOE24', 'GEMSDOE25', 'GEMSDOE27', 'GEMSDOE28', 'GEMSDOE30', 'GEMSDOE31', 'GEMSDOE32', 'GEMSDOE33', 'GEMSDOE36'];

function focusPage(site) {
  const file = path.join(docs, 'focus', `${site}.html`);
  assert.ok(fs.existsSync(file), `${site}: executive-summary page exists`);
  const html = fs.readFileSync(file, 'utf8');
  const dom = new JSDOM(html, {url: `https://example.test/docs/focus/${site}.html`});
  return {dom, text: dom.window.document.body.textContent.replace(/\s+/g, ' ').trim()};
}

test('the nine requested sites each have a fail-closed, evidence-linked executive summary', () => {
  const pageFiles = fs.readdirSync(path.join(docs, 'focus')).filter(name => name.endsWith('.html')).sort();
  assert.deepEqual(pageFiles, expectedSites.map(site => `${site}.html`).sort());
  assert.deepEqual(focusSites.map(row => row.site).sort(), [...expectedSites].sort());

  const geometryRows = new Map(geometry.historical_final_dots.map(row => [row.site, row]));
  for (const site of expectedSites) {
    const record = focusSites.find(row => row.site === site);
    const measured = geometryRows.get(site);
    assert.ok(record && measured, `${site}: matching pinned scorecard and geometry receipt`);
    assert.equal(record.sha256, measured.sha256, `${site}: file hash matches measured raster`);
    assert.equal(measured.literal_result, 'DUPLICATE_STOP', `${site}: literal uniqueness gate remains negative`);

    const {dom, text} = focusPage(site);
    const doc = dom.window.document;
    const badge = doc.querySelector('.header .badge');
    assert.equal(badge?.textContent.trim(), 'OK TO SUBMIT: NO', `${site}: prominent submit status`);
    assert.ok(doc.querySelector('h2')?.textContent.includes(`${site} executive summary — DO NOT RESUBMIT`));
    assert.ok(text.includes(record.file), `${site}: summary names its exact historical file`);
    assert.ok(text.includes(`${record.owner_reported_unverified.toFixed(4)} — USER-REPORTED / UNVERIFIED`));
    assert.match(text, /Estimated leaderboard score:\s*unavailable/i);
    assert.match(text, /Unique:\s*NO/);
    assert.ok(text.includes(`${(measured.max_focus_overlap_fraction * 100).toFixed(1)}% of its dots are within 3 px of ${measured.closest_focus_site}`));
    assert.match(text, /DUPLICATE_STOP/);
    assert.match(text, /research reference only/i);
    assert.doesNotMatch(text, /OK TO SUBMIT:\s*YES/i);
    assert.equal(doc.querySelectorAll('a[download]').length, 0, `${site}: historical file is not presented as an approved local download`);

    const rasterRows = manifest.filter(row => row.repo === site && row.sha256 === record.sha256);
    assert.equal(rasterRows.length, 1, `${site}: one hash-pinned source row`);
    const source = `https://github.com/buffedlizard55-lab/${site}/raw/${rasterRows[0].ref}/${rasterRows[0].path}`;
    const rasterLinks = [...doc.querySelectorAll('a[href]')].filter(link => link.href === source);
    assert.equal(rasterLinks.length, 1, `${site}: historical file links to its hash-pinned source`);
    assert.match(rasterLinks[0].parentElement.textContent, /research reference only/i);
    assert.ok(text.includes(measured.sha256), `${site}: page exposes the audited raster SHA-256`);
    dom.window.close();
  }
});
