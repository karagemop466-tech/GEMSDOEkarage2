'use strict';
const button = document.getElementById('refresh-sources');
if (button) button.addEventListener('click', async () => {
  button.disabled = true;
  const status = document.getElementById('freshness-status');
  const results = document.getElementById('freshness-results');
  status.textContent = 'Checking public GitHub commits only. No competition account or leaderboard is accessed.';
  results.replaceChildren();
  try {
    const snapshotResponse = await fetch('evidence/freshness.json');
    if (!snapshotResponse.ok) throw new Error('Local snapshot unavailable');
    const snapshot = await snapshotResponse.json();
    const rows = await Promise.all(Object.entries(snapshot.refs).map(async ([repo, ref]) => {
      try {
        const response = await fetch(`https://api.github.com/repos/buffedlizard55-lab/${encodeURIComponent(repo)}/commits/main`, {headers: {Accept:'application/vnd.github+json'}});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const current = await response.json();
        if (typeof current.sha !== 'string' || !/^[a-f0-9]{40}$/.test(current.sha)) throw new Error('Invalid GitHub response');
        return `${repo}: ${current.sha === ref ? 'matches pinned revision' : 'NEW REVISION — audit snapshot is stale; no automatic clearance'}`;
      } catch (error) { return `${repo}: freshness unverified (${error.message})`; }
    }));
    const list = document.createElement('ul');
    rows.forEach(text => {const item=document.createElement('li'); item.textContent=text; list.appendChild(item);});
    results.appendChild(list);
    status.textContent = `Checked ${new Date().toISOString()}. Commit freshness is not score or uniqueness verification.`;
  } catch (error) { status.textContent = `Freshness not verified: ${error.message}. Retaining the pinned evidence, without claiming it is current.`; }
  finally { button.disabled=false; }
});
