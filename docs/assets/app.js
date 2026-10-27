/* Public read-only dashboard. Scientific and selector gates are never inferred from UI data. */
(() => {
  "use strict";
  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };
  const link = (url, text, className) => {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:" || parsed.hostname !== "github.com") throw new Error("Untrusted historical link");
    const a = el("a", className, text);
    a.href = parsed.href; a.target = "_blank"; a.rel = "noopener noreferrer";
    return a;
  };
  const percent = value => `${(value * 100).toFixed(2)}%`;
  const validateAudit = data => {
    const names = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"];
    if (!data || !Array.isArray(data.sites) || data.sites.length !== names.length) throw new Error("Incomplete audit");
    const seen = new Set();
    for (const site of data.sites) {
      if (!names.includes(site.site) || seen.has(site.site)) throw new Error("Invalid audit site");
      seen.add(site.site);
      if (typeof site.reported_score !== "number" || !Number.isFinite(site.reported_score) || site.reported_score < 0 || site.reported_score > 1 ||
          typeof site.max_other_site_overlap !== "number" || !Number.isFinite(site.max_other_site_overlap) || site.max_other_site_overlap < 0 || site.max_other_site_overlap > 1 ||
          !names.includes(site.max_overlap_reference) || site.max_overlap_reference === site.site ||
          typeof site.unique_vs_eight_historical !== "boolean" || site.submit !== false || site.score_estimate !== null ||
          !/^[a-f0-9]{64}$/.test(site.sha256 || "") || typeof site.filename !== "string") throw new Error("Invalid audit record");
    }
  };
  const siteLine = (tag, site) => {
    const a = el(tag, "site-name", site.site);
    if (tag === "a") a.href = `executive-summary.html#${encodeURIComponent(site.site)}`;
    return a;
  };
  const buildRow = site => {
    const row = el("tr");
    const file = el("td"); file.append(siteLine("a", site), el("span", "file-name", site.filename)); row.append(file);
    const score = el("td"); score.append(el("span", "score-value", Number(site.reported_score).toFixed(4)), el("span", "sub-label", "USER-REPORTED · UNVERIFIED")); row.append(score);
    const estimate = el("td"); estimate.append(el("span", "", "Not estimable"), el("span", "sub-label", "No validated transfer")); row.append(estimate);
    const unique = el("td"); unique.append(el("span", "not-unique", site.unique_vs_eight_historical ? "Not established" : "No"), el("span", "sub-label", `${percent(site.max_other_site_overlap)} vs ${site.max_overlap_reference}`)); row.append(unique);
    const action = el("td"); action.append(link(site.research_download_url, "Research file ↗", "research-link"), el("span", "sub-label", "DO NOT SUBMIT")); row.append(action);
    return row;
  };
  const buildDetail = site => {
    const card = el("article", "site-detail"); card.id = site.site;
    const head = el("div", "detail-head"); head.append(el("h3", "", site.site), el("span", "", "DO NOT SUBMIT"));
    card.append(head, el("p", "detail-score", Number(site.reported_score).toFixed(4)), el("p", "detail-copy", "USER-REPORTED / UNVERIFIED · leaderboard estimate unavailable"));
    card.append(link(site.research_download_url, site.filename, "detail-file"));
    const archive = el("a", "detail-file", "Detailed per-site review ↗");
    archive.href = `site-${encodeURIComponent(site.site)}.html`;
    card.append(archive);
    const novelty = site.unique_vs_eight_historical ? "No duplicate found among selected files; full registry not checked" : "Not unique vs selected historical files";
    card.append(el("p", "detail-foot", `${novelty}: ${percent(site.max_other_site_overlap)} within 3 px of ${site.max_overlap_reference}. SHA-256 ${site.sha256.slice(0, 16)}…`));
    return card;
  };
  const loadAudit = async () => {
    const target = document.getElementById("scorecard-body"), details = document.getElementById("site-detail-list");
    if (!target && !details) return;
    try {
      const response = await fetch("data/focus_audit.json", {cache: "no-cache"});
      if (!response.ok) throw new Error("Audit unavailable");
      const data = await response.json();
      validateAudit(data);
      if (target) target.replaceChildren(...data.sites.map(buildRow));
      if (details) {
        details.replaceChildren(...data.sites.map(buildDetail));
        const hash = decodeURIComponent(location.hash.slice(1));
        const anchor = /^GEMSDOE\d+$/.test(hash) ? document.getElementById(hash) : null;
        if (anchor && typeof anchor.scrollIntoView === "function") anchor.scrollIntoView();
      }
    } catch (_) {
      if (target) { const row = el("tr"), cell = el("td", "loading-cell", "Audit could not be loaded. Do not submit; see the linked JSON."); cell.colSpan = 5; row.append(cell); target.replaceChildren(row); }
      if (details) details.replaceChildren(el("p", "loading-cell", "Audit could not be loaded. Do not submit; see the linked JSON."));
    }
  };
  const loadMonitor = async () => {
    const score = document.getElementById("leaderboard-score"), status = document.getElementById("leaderboard-status");
    if (!score || !status) return;
    try {
      const response = await fetch("data/monitor.json", {cache: "no-cache"});
      if (!response.ok) throw new Error("Monitor unavailable");
      const data = await response.json();
      const note = document.getElementById("table-note");
      if (note && Array.isArray(data.sites) && data.sites.length) {
        const changed = data.sites.filter(s => s.status === "changed").length;
        const unknown = data.sites.filter(s => s.status === "unavailable").length;
        const checkedAt = new Date(data.generated_utc || "");
        const hours = (Date.now() - checkedAt.valueOf()) / 3600000;
        const stale = Number.isNaN(checkedAt.valueOf()) || hours > 8 || hours < -0.25;
        note.textContent = `Nine historical files only; not the full registry. Source-head check${stale ? " (STALE)" : ""}: ${changed} changed, ${unknown} unavailable at ${data.generated_utc || "unknown time"}.`;
      }
      const board = data.leaderboard || {};
      if (!["ok", "snapshot", "unavailable"].includes(board.status)) throw new Error("Unknown monitor status");
      const snapshot = board.status === "unavailable" ? board.last_successful : board;
      if (!snapshot || !/^(0(?:\.\d+)?|1(?:\.0+)?)$/.test(snapshot.score_text || "")) throw new Error("No valid score snapshot");
      const checked = new Date(snapshot.checked_utc);
      if (Number.isNaN(checked.valueOf())) throw new Error("No valid timestamp");
      const ageHours = (Date.now() - checked.valueOf()) / 3600000;
      score.textContent = snapshot.score_text;
      const stale = board.status === "unavailable" || ageHours > 8 || ageHours < -0.25;
      const label = stale ? "STALE SNAPSHOT" : "DATED SNAPSHOT";
      status.textContent = `${label} / CHECK OFFICIAL BOARD · ${checked.toISOString().slice(0, 16).replace("T", " ")} UTC`;
    } catch (_) { score.textContent = "—"; status.textContent = "SNAPSHOT UNAVAILABLE · SEE OFFICIAL BOARD"; }
  };
  loadAudit(); loadMonitor();
})();
