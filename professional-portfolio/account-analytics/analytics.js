/* Account Analyst Portfolio Showcase — public synthetic-data edition 1.0.0.
 * Copyright © 2026 Gateway Information Group LLC. All rights reserved.
 * One calculation implementation, used by the browser and regression tests.
 */
"use strict";
const AccountAnalytics = (() => {
  const regions = Object.freeze({"Client A": "North", "Client B": "Central", "Client C": "South"});
  const thresholds = Object.freeze({Motion: 15000, Digital: 10000, Print: 8000});
  // Invented fixtures. These are not anonymized client records or measured savings.
  const rows = Object.freeze([
    ["DEMO-01", "Client A", "Motion", 25000, 2500, 500],
    ["DEMO-02", "Client A", "Digital", 12000, 1200, 300],
    ["DEMO-03", "Client A", "Print", 8000, null, 400],
    ["DEMO-04", "Client B", "Motion", 18000, 1800, 200],
    ["DEMO-05", "Client B", "Digital", 9000, 0, 0],
    ["DEMO-06", "Client B", "Print", 6000, 600, 150],
    ["DEMO-07", "Client C", "Motion", 30000, 3000, 1000],
    ["DEMO-08", "Client C", "Digital", 10000, 1000, null],
    ["DEMO-09", "Client C", "Print", 7500, 750, 250],
    ["DEMO-10", "Client A", "Motion", 15000, 1500, 500],
    ["DEMO-11", "Client B", "Digital", 14000, 1400, 600],
    ["DEMO-12", "Client C", "Print", 11000, 1100, 400]
  ].map(([id, client, type, spend, hard, soft]) => Object.freeze({id, client, type, spend, hard, soft})));

  function analyze(input = rows, filter = {}) {
    if (!Array.isArray(input) || input.length > 1000) throw new Error("Expected at most 1000 records.");
    if (!filter || typeof filter !== "object" || Array.isArray(filter)) throw new Error("Invalid filter.");
    const allowed = {client: ["All", ...Object.keys(regions)], type: ["All", ...Object.keys(thresholds)], quality: ["All", "Complete", "Review"]};
    for (const key of Object.keys(filter)) {
      if (!Object.hasOwn(allowed, key) || !allowed[key].includes(filter[key])) throw new Error("Unknown filter.");
    }
    const seen = new Set();
    const validMoney = (x) => Number.isSafeInteger(x) && x >= 0 && x <= 1000000;
    const normalized = input.map((r) => {
      if (!r || typeof r !== "object" || typeof r.id !== "string" || !/^DEMO-\d{2,4}$/.test(r.id) || seen.has(r.id)) throw new Error("Invalid or duplicate demo ID.");
      seen.add(r.id);
      if (!Object.hasOwn(regions, r.client) || !Object.hasOwn(thresholds, r.type)) throw new Error("Unknown lookup value.");
      if (!validMoney(r.spend) || ![r.hard, r.soft].every(x => x === null || validMoney(x))) throw new Error("Invalid money value.");
      if ((r.hard ?? 0) + (r.soft ?? 0) > r.spend) throw new Error("Savings exceed reviewed spend.");
      const complete = r.hard !== null && r.soft !== null;
      return {...r, region: regions[r.client], quality: complete ? "Complete" : "Review", low: r.spend <= thresholds[r.type], savings: complete ? r.hard + r.soft : null};
    });
    const selected = normalized.filter(r => Object.entries(filter).every(([k, v]) => v === "All" || r[k] === v));
    const summarize = (items) => {
      const complete = items.filter(r => r.quality === "Complete");
      const spend = items.reduce((s, r) => s + r.spend, 0);
      const eligibleSpend = complete.reduce((s, r) => s + r.spend, 0);
      const savings = complete.reduce((s, r) => s + r.savings, 0);
      return {count: items.length, complete: complete.length, review: items.length - complete.length, spend, eligibleSpend, savings, rate: eligibleSpend > 0 ? savings / eligibleSpend : null, low: items.filter(r => r.low).length};
    };
    return {rows: selected, totals: summarize(selected), clients: Object.keys(regions).map(client => ({client, ...summarize(selected.filter(r => r.client === client))}))};
  }
  return Object.freeze({version: "1.0.0", rows, regions, thresholds, analyze});
})();
if (typeof module !== "undefined" && module.exports) module.exports = AccountAnalytics;

if (typeof document !== "undefined") {
  const money = (x) => x === null ? "Missing" : new Intl.NumberFormat("en-US", {style: "currency", currency: "USD", maximumFractionDigits: 0}).format(x);
  const percent = (x) => x === null ? "Not available" : `${(x * 100).toFixed(1)}%`;
  const put = (id, value) => { document.getElementById(id).textContent = value; };
  const tableRow = (parent, values) => {
    const tr = document.createElement("tr");
    values.forEach((value, index) => { const td = document.createElement(index === 0 ? "th" : "td"); if (index === 0) td.scope = "row"; td.textContent = value; tr.appendChild(td); });
    parent.appendChild(tr);
  };
  function render() {
    try {
      const filter = Object.fromEntries(["client", "type", "quality"].map(key => [key, document.getElementById(key).value]));
      const result = AccountAnalytics.analyze(AccountAnalytics.rows, filter), t = result.totals;
      put("count", t.count); put("spend", money(t.spend)); put("savings", money(t.savings)); put("rate", percent(t.rate)); put("review", t.review); put("low", t.low);
      put("status", `${t.count} synthetic projects shown. ${t.complete} complete; ${t.review} need review. Savings rate uses ${money(t.eligibleSpend)} of complete-record spend, not all spend.`);
      const body = document.getElementById("records"); body.replaceChildren();
      result.rows.forEach(r => tableRow(body, [r.id, r.client, r.type, r.region, money(r.spend), money(r.hard), money(r.soft), r.savings === null ? "Excluded" : money(r.savings), r.low ? "Yes" : "No", r.quality]));
      if (!result.rows.length) tableRow(body, ["No matching records", "", "", "", "", "", "", "", "", ""]);
      const groups = document.getElementById("groups"); groups.replaceChildren();
      result.clients.forEach(g => tableRow(groups, [g.client, g.count, g.complete, money(g.spend), money(g.savings), percent(g.rate)]));
      const chart = document.getElementById("bars"); chart.replaceChildren();
      const max = Math.max(1, ...result.clients.map(g => g.savings));
      result.clients.forEach(g => {
        const line = document.createElement("div"); line.className = "bar-row";
        const label = document.createElement("span"); label.textContent = g.client;
        const bar = document.createElement("meter"); bar.min = 0; bar.max = max; bar.value = g.savings; bar.setAttribute("aria-label", `${g.client}, complete-record savings ${money(g.savings)}`);
        const value = document.createElement("strong"); value.textContent = money(g.savings);
        line.append(label, bar, value); chart.appendChild(line);
      });
      put("error", "");
    } catch (err) {
      ["count", "spend", "savings", "rate", "review", "low"].forEach(id => put(id, "Not available"));
      ["records", "groups", "bars"].forEach(id => document.getElementById(id).replaceChildren());
      put("status", "No current result: the selected input could not be validated.");
      put("error", "Demo could not calculate. Reset filters or reload the page to restore the bundled synthetic example.");
    }
  }
  ["client", "type", "quality"].forEach(id => document.getElementById(id).addEventListener("change", render));
  document.getElementById("reset").addEventListener("click", () => { ["client", "type", "quality"].forEach(id => {document.getElementById(id).value = "All";}); render(); });
  render();
}
