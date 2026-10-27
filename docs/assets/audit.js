/* Public repository freshness only. This never checks a private score or authorizes upload. */
(function (root) {
  "use strict";
  function classify(pinned, actual) {
    if (!/^[a-f0-9]{40}$/.test(pinned || "") || !/^[a-f0-9]{40}$/.test(actual || "")) return "unavailable";
    return pinned === actual ? "current" : "stale";
  }
  async function checkReference(fetcher, entry) {
    if (!/^GEMSDOE(?:24|25|27|28|30|31|32|33|36)$/.test(entry.site || "")) return {site: entry.site, state:"unavailable"};
    const controller = typeof AbortController === "function" ? new AbortController() : null;
    const timer = controller ? setTimeout(() => controller.abort(), 10000) : null;
    try {
      const response = await fetcher("https://api.github.com/repos/buffedlizard55-lab/" + entry.site + "/commits/main", {
        headers: {"Accept": "application/vnd.github+json"}, cache: "no-store",
        ...(controller ? {signal: controller.signal} : {})
      });
      if (!response.ok) throw new Error("Source lookup failed");
      const json = await response.json();
      return {site: entry.site, state: classify(entry.pinned_ref, json.sha)};
    } catch (_error) {
      return {site: entry.site, state:"unavailable"};
    } finally {
      if (timer !== null) clearTimeout(timer);
    }
  }
  if (typeof module === "object" && module.exports) module.exports = {classify, checkReference};
  if (!root || !root.document) return;
  const doc = root.document;
  async function refresh() {
    const button = doc.querySelector("[data-refresh]");
    const summary = doc.querySelector("[data-feed-summary]");
    if (!button || !summary) return;
    button.disabled = true;
    summary.textContent = "Checking public repository commits…";
    try {
      const response = await root.fetch("data/reference-audit.json", {cache:"no-store"});
      if (!response.ok) throw new Error("Audit unavailable");
      const audit = await response.json();
      const refs = audit.reference_files;
      if (!Array.isArray(refs) || refs.length !== 9) throw new Error("Incomplete snapshot");
      const checks = await Promise.all(refs.map((entry) => checkReference(root.fetch.bind(root), entry)));
      checks.forEach((item) => {
        if (!/^GEMSDOE(?:24|25|27|28|30|31|32|33|36)$/.test(item.site || "")) return;
        const row = doc.querySelector('[data-site="' + item.site + '"]');
        const slot = row && row.querySelector("[data-freshness]");
        if (!slot) return;
        slot.className = "fresh " + item.state;
        slot.textContent = item.state === "current" ? "Source unchanged" : item.state === "stale" ? "Changed since audit" : "Check unavailable";
      });
      const stale = checks.filter((x) => x.state === "stale").length;
      const unavailable = checks.filter((x) => x.state === "unavailable").length;
      summary.textContent = "Checked " + new Date().toLocaleString() + ": " + (checks.length - unavailable) + " checked; " + stale + " change(s) detected; " + unavailable + " unavailable. A changed source is not re-audited.";
    } catch (_error) {
      summary.textContent = "Freshness check unavailable. The pinned audit remains a dated snapshot.";
      doc.querySelectorAll("[data-freshness]").forEach((slot) => {slot.className = "fresh unavailable"; slot.textContent = "Check unavailable";});
    } finally {
      button.disabled = false;
    }
  }
  doc.addEventListener("DOMContentLoaded", () => {
    const button = doc.querySelector("[data-refresh]");
    if (button) { button.addEventListener("click", refresh); refresh(); }
  });
})(typeof window !== "undefined" ? window : null);
