/* End-to-end static-site smoke test with deterministic public-API responses. */
const assert = require('node:assert/strict');
const child = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const crypto = require('node:crypto');
const chromium = require('@sparticuz/chromium').default;
const {chromium: playwright} = require('playwright-core');
const root = path.resolve(__dirname, '..');
const audit = require('../docs/data/reference-audit.json');

async function startSite() {
  const server = child.spawn('python3', [path.join(root, 'scripts/serve_site.py'), '--host', '127.0.0.1', '--port', '0'], {cwd:root});
  let logs = '';
  const port = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Preview server did not start: ' + logs)), 10000);
    server.stdout.on('data', data => {
      logs += data;
      const match = logs.match(/Serving published files on 127\.0\.0\.1:(\d+)/);
      if (match) {clearTimeout(timer); resolve(Number(match[1]));}
    });
    server.stderr.on('data', data => { logs += data; });
    server.on('exit', code => {clearTimeout(timer); reject(new Error('Preview exited ' + code + ': ' + logs));});
  }).catch(error => {server.kill(); throw error;});
  return {server, port};
}

function chromeEnvironment() {
  // On minimal sandboxes, use the packaged Amazon Linux NSS libraries. No
  // browser download or system package installation is needed at test time.
  const chromePackageRoot = path.resolve(path.dirname(require.resolve('@sparticuz/chromium')), '..');
  const archive = path.join(chromePackageRoot, 'bin/al2023.tar.br');
  const runtime = path.join(root, '.cache/browser-runtime');
  fs.mkdirSync(runtime, {recursive:true});
  if (!fs.existsSync(path.join(runtime, 'lib/libnss3.so'))) {
    const tar = zlib.brotliDecompressSync(fs.readFileSync(archive));
    child.execFileSync('tar', ['-xf', '-', '-C', runtime], {input:tar});
  }
  return {...process.env, LD_LIBRARY_PATH: path.join(runtime, 'lib') + (process.env.LD_LIBRARY_PATH ? ':' + process.env.LD_LIBRARY_PATH : '')};
}

(async () => {
  const {server, port} = await startSite();
  let browser;
  try {
    const base = `http://127.0.0.1:${port}`;
    assert.equal((await fetch(base + '/.git/config')).status, 404);
    assert.equal((await fetch(base + '/.cache/research/inputs/sample.tif')).status, 404);
    assert.equal((await fetch(base + '/research/')).status, 403);
    browser = await playwright.launch({executablePath:await chromium.executablePath(), args:chromium.args, headless:true, env:chromeEnvironment()});
    const page = await browser.newPage({viewport:{width:1440, height:1050}, deviceScaleFactor:1});
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    let network = 'ok';
    await page.route('https://api.github.com/repos/buffedlizard55-lab/**', async route => {
      if (network === 'fail') return route.abort();
      const match = route.request().url().match(/(GEMSDOE\d+)\/commits\/main$/);
      const row = match && audit.reference_files.find(item => item.site === match[1]);
      assert.ok(row, 'Only known reference repositories may be checked');
      const sha = network === 'stale' && row.site === 'GEMSDOE32' ? 'f'.repeat(40) : row.pinned_ref;
      await route.fulfill({status:200, contentType:'application/json', headers:{'access-control-allow-origin':'*'}, body:JSON.stringify({sha})});
    });
    const parallelCard = require('../evidence/run_card.json');
    const artifactResponse = await fetch(base + '/' + parallelCard.raster);
    assert.equal(artifactResponse.status, 200);
    const artifactHash = crypto.createHash('sha256').update(Buffer.from(await artifactResponse.arrayBuffer())).digest('hex');
    assert.equal(artifactHash, parallelCard.raster_sha256);
    assert.equal(parallelCard.approved_for_weekly_slot, false);
    // HK3 is an existing research-only file, never an upload candidate.
    const hk3 = require('../evidence/hk3/run_card.json');
    const hk3Response = await fetch(base + '/' + hk3.raster.file);
    assert.equal(hk3Response.status, 200);
    assert.equal(crypto.createHash('sha256').update(Buffer.from(await hk3Response.arrayBuffer())).digest('hex'), hk3.raster.sha256);
    assert.equal(hk3.verdict, 'negative');
    const expectBadge = 'OK TO SUBMIT: NO';
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width, height:900});
      await page.goto(base + '/', {waitUntil:'domcontentloaded'});
      await page.waitForURL('**/docs/index.html');
      assert.equal((await page.locator('.header .badge').innerText()).trim(), expectBadge);
      // The desk may offer a verified current candidate (evidence/k10) above the HK3 research
      // control, so the research-only link is addressed by href rather than by position -- the
      // same contract tests/test_hk3.py states. Everything below still asserts on the HK3 file:
      // its RESEARCH ONLY wording, the downloaded filename and its SHA-256.
      const primary = page.locator(`a.btn.big[download][href*="${hk3.submission.name}"]`).first();
      assert.ok(await primary.count(), 'HK3 research download is no longer offered by the desk');
      for (const link of await page.locator('a.btn.big[download]').all()) {
        assert.ok((await link.getAttribute('href')).startsWith('downloads/'), 'a download link leaves the published tree');
      }
      assert.ok((await primary.innerText()).includes('RESEARCH ONLY'));
      const [download] = await Promise.all([page.waitForEvent('download'), primary.click()]);
      assert.equal(download.suggestedFilename(), path.basename(hk3.raster.file));
      const downloaded = fs.readFileSync(await download.path());
      assert.equal(crypto.createHash('sha256').update(downloaded).digest('hex'), hk3.raster.sha256);
      assert.ok((await page.locator('#legacy').innerText()).includes('DO NOT SUBMIT'));
      assert.ok((await page.locator('body').innerText()).includes('not unique'));
      assert.equal(await page.locator('#nine-sites tbody tr').count(), 9);
      assert.ok(await page.locator('a[href="audit.html"]').count());
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Desk overflow');
      console.log(`PASS ${width}px: negative badge, research-only click/download, exact SHA-256`);
    }
    for (const viewport of [{width:1440,height:1050}, {width:390,height:844}]) {
      await page.setViewportSize(viewport);
      await page.goto(base + '/docs/audit.html', {waitUntil:'domcontentloaded'});
      await page.waitForFunction(() => document.querySelector('[data-feed-summary]').textContent.includes('checked;'));
      assert.equal(await page.locator('tbody tr[data-site]').count(), 9);
      assert.equal(await page.locator('a[download]').count(), 0);
      assert.ok((await page.locator('body').innerText()).includes('The verdict lives on the submission desk'));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Overview overflow');
      await page.locator('[data-site="GEMSDOE32"] .site-link').click();
      assert.ok(page.url().endsWith('/docs/sites/GEMSDOE32.html'));
      assert.ok((await page.locator('body').innerText()).toLowerCase().includes('gemsdoe32'));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Site detail overflow');
      await page.goBack();
      await page.locator('a[href="submit.html"]').first().click();
      assert.ok(page.url().endsWith('/docs/submit.html'));
      assert.ok((await page.locator('body').innerText()).toLowerCase().includes('do not submit'));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Submit page overflow');
      await page.goto(base + '/docs/audit-research.html');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Research page overflow');
      console.log(`PASS ${viewport.width}px: navigation, 9 rows, release lock, no viewport overflow`);
    }
    // Legacy and alternate routes must not revive the previously unsafe
    // invitation to download and submit a research-only TIFF.
    await page.goto(base + '/docs/how-to-submit.html', {waitUntil:'domcontentloaded'});
    assert.equal((await page.locator('.header .badge').innerText()).trim(), expectBadge);
    assert.ok((await page.locator('body').innerText()).toLowerCase().includes('do not submit'));
    await page.goto(base + '/docs/executive-summary.html', {waitUntil:'domcontentloaded'});
    assert.equal((await page.locator('.header .badge').innerText()).trim(), expectBadge);
    assert.ok((await page.locator('body').innerText()).includes('0.2778'));
    await page.goto(base + '/docs/focus/GEMSDOE32.html', {waitUntil:'domcontentloaded'});
    const focusText = await page.locator('body').innerText();
    assert.ok(focusText.includes('GEMSDOE32') && focusText.includes('DO NOT RESUBMIT'));
    assert.ok(focusText.includes('USER-REPORTED / UNVERIFIED'));
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, 'Focus page overflow');
    await page.goto(base + '/docs/site-GEMSDOE32.html', {waitUntil:'domcontentloaded'});
    await page.waitForURL('**/docs/sites/GEMSDOE32.html');
    assert.ok((await page.locator('body').innerText()).includes('GEMSDOE32'));
    await page.goto(base + '/docs/research-hypotheses.html', {waitUntil:'domcontentloaded'});
    await page.waitForURL('**/docs/hypotheses.html');
    assert.ok((await page.locator('body').innerText()).includes('H1 · Signed downthrow parity'));

    network = 'stale';
    await page.goto(base + '/docs/audit.html');
    await page.waitForFunction(() => document.querySelector('[data-site="GEMSDOE32"] [data-freshness]').textContent === 'Changed since audit');
    assert.ok((await page.locator('[data-feed-summary]').innerText()).includes('1 change(s) detected'));
    network = 'fail';
    await page.locator('[data-refresh]').click();
    await page.waitForFunction(() => document.querySelector('[data-feed-summary]').textContent.includes('9 unavailable'));
    assert.equal(await page.locator('[data-refresh]').isEnabled(), true);
    assert.equal(await page.locator('.fresh.unavailable').count(), 9);
    await page.goto(base + '/docs/experiment-index.html');
    await page.locator('#refresh-sources').click();
    await page.waitForFunction(() => document.querySelector('#freshness-results').textContent.includes('freshness unverified'));
    assert.equal(await page.locator('#refresh-sources').isEnabled(), true);
    assert.deepEqual(errors, []);
    console.log('PASS freshness: current, changed and unavailable fail-safe states');
  } finally {
    if (browser) await browser.close();
    server.kill();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
