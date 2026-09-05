/* Copyright © 2026 Gateway Information Group LLC. All rights reserved. */
const test = require('node:test');
const assert = require('node:assert/strict');
const a = require('../professional-portfolio/account-analytics/analytics.js');
test('all synthetic totals reconcile', () => {
  const t = a.analyze().totals;
  assert.deepEqual({...t, rate: null}, {count:12, complete:10, review:2, spend:165500, eligibleSpend:147500, savings:17750, rate:null, low:6});
  assert.equal(t.rate, 17750/147500);
});
test('missing savings remain excluded, not zero', () => {
  const r = a.analyze(a.rows, {quality:'Review'});
  assert.equal(r.totals.count, 2); assert.equal(r.totals.eligibleSpend, 0); assert.equal(r.totals.rate, null);
  assert.ok(r.rows.every(x => x.savings === null));
});
test('genuine zero savings are complete', () => {
  const r = a.analyze([a.rows[4]]);
  assert.equal(r.totals.complete,1); assert.equal(r.totals.rate,0); assert.equal(r.totals.eligibleSpend,9000);
});
test('threshold is inclusive and type specific', () => {
  assert.equal(a.analyze([a.rows[9]]).rows[0].low, true);
  assert.equal(a.analyze([{...a.rows[9],spend:15001}]).rows[0].low, false);
});
test('client and type filters compose', () => {
  const r=a.analyze(a.rows,{client:'Client A',type:'Motion'});
  assert.equal(r.totals.count,2); assert.equal(r.totals.savings,5000);
  assert.ok(r.rows.every(x => x.region === 'North'));
});
test('empty view has no fabricated rate', () => {
  const t=a.analyze(a.rows,{client:'Client B',quality:'Review'}).totals;
  assert.equal(t.count,0); assert.equal(t.rate,null);
});
test('group sums match all-record totals', () => {
  const r=a.analyze();
  for(const key of ['count','complete','review','spend','eligibleSpend','savings','low']) assert.equal(r.clients.reduce((s,g)=>s+g[key],0),r.totals[key]);
});
test('invalid and duplicate input fails closed', () => {
  for(const bad of [-1,NaN,Infinity,'25000',0.5,1000001]) assert.throws(()=>a.analyze([{...a.rows[0],spend:bad}]));
  assert.throws(()=>a.analyze([a.rows[0],a.rows[0]]));
  assert.throws(()=>a.analyze([{...a.rows[0],client:'Unknown'}]));
  assert.throws(()=>a.analyze([{...a.rows[0],hard:30000}]));
  assert.throws(()=>a.analyze(new Array(1001).fill(a.rows[0])));
});
test('unknown filters are rejected rather than ignored', () => {
  assert.throws(()=>a.analyze(a.rows,{typo:'All'}));
  assert.throws(()=>a.analyze(a.rows,{client:'Unknown'}));
  assert.throws(()=>a.analyze(a.rows,null));
});
test('analysis does not mutate fixtures', () => {
  const before=JSON.stringify(a.rows); a.analyze(a.rows,{client:'Client C'});
  assert.equal(JSON.stringify(a.rows),before); assert.ok(Object.isFrozen(a.rows));
  assert.ok(a.rows.every(Object.isFrozen));
});
test('all filter combinations reconcile and stay bounded', () => {
  for(const client of ['All',...Object.keys(a.regions)]) for(const type of ['All',...Object.keys(a.thresholds)]) for(const quality of ['All','Complete','Review']) {
    const r=a.analyze(a.rows,{client,type,quality});
    assert.equal(r.totals.count,r.rows.length); assert.equal(r.totals.complete+r.totals.review,r.totals.count);
    assert.ok(r.totals.count<=12); assert.ok(r.totals.savings<=r.totals.eligibleSpend);
  }
});
