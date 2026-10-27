const test = require('node:test');
const assert = require('node:assert/strict');
const {classify, checkReference} = require('../docs/assets/audit.js');
const pin = 'a'.repeat(40);

test('classifies unchanged, changed and invalid hashes without guessing', () => {
  assert.equal(classify(pin, pin), 'current');
  assert.equal(classify(pin, 'b'.repeat(40)), 'stale');
  assert.equal(classify(pin, ''), 'unavailable');
  assert.equal(classify('invalid', pin), 'unavailable');
});

test('fetches only the allowed public repository for a pinned reference', async () => {
  let requested;
  const result = await checkReference(async (url) => {
    requested = url;
    return {ok: true, json: async () => ({sha: pin})};
  }, {site: 'GEMSDOE24', pinned_ref: pin});
  assert.equal(requested, 'https://api.github.com/repos/buffedlizard55-lab/GEMSDOE24/commits/main');
  assert.deepEqual(result, {site:'GEMSDOE24', state:'current'});
});

test('network, authorization and invalid data fail to unavailable', async () => {
  assert.equal((await checkReference(async () => { throw new Error('network'); }, {site:'GEMSDOE32', pinned_ref:pin})).state, 'unavailable');
  assert.equal((await checkReference(async () => ({ok:false}), {site:'GEMSDOE32', pinned_ref:pin})).state, 'unavailable');
  assert.equal((await checkReference(async () => ({ok:true, json:async () => ({sha:'bad'})}), {site:'GEMSDOE32', pinned_ref:pin})).state, 'unavailable');
  let invoked = false;
  const bad = await checkReference(async () => {invoked = true;}, {site:'../../other', pinned_ref:pin});
  assert.equal(bad.state, 'unavailable');
  assert.equal(invoked, false);
});
