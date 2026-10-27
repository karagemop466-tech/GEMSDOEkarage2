(() => {
  const target = document.getElementById("feed-status");
  if (!target) return;
  fetch("data/source-feed.json", { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("feed unavailable");
      return response.json();
    })
    .then((feed) => {
      const timestamp = new Date(feed.checked_utc);
      const summary = feed.summary;
      if (Number.isNaN(timestamp.getTime()) || !summary ||
          !Number.isInteger(summary.total) || !Number.isInteger(summary.changed) ||
          !Number.isInteger(summary.unavailable)) throw new Error("invalid feed");
      const age = Date.now() - timestamp.getTime();
      const stale = age < -300000 || age > 18 * 60 * 60 * 1000;
      const when = timestamp.toISOString().replace("T", " ").slice(0, 16) + " UTC";
      target.textContent = `Checked ${when} · ${summary.changed} changed · ${summary.unavailable} unavailable of ${summary.total} sites${stale ? " · STALE" : ""}.`;
    })
    .catch(() => { target.textContent = "Source feed unavailable. Do not assume the review is current."; });
})();
