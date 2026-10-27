// Private staging worker. HmemClient owns durable publication and locks.
// The official upstream engine is imported unchanged; no model operations.
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';

const assert = (v: unknown): void => { if (!v) throw new Error('invalid'); };
const exact = (v: any, fields: string[]) => assert(v && typeof v === 'object' &&
  !Array.isArray(v) && Object.keys(v).sort().join(',') === fields.sort().join(','));
const text = (v: any, max: number) => assert(typeof v === 'string' && v.length > 0 && v.length <= max);
const publicMemory = (m: any) => Object.fromEntries(
  ['id', 'content', 'source', 'chatId', 'tags', 'provenance', 'timestamp'].map(k => [k, m[k]]));
const inputFields = ['content', 'type', 'layer', 'tags', 'confidence', 'source', 'provenance', 'chatId'];

async function main() {
  process.umask(0o077);
  const raw = fs.readFileSync(0, 'utf8');
  assert(Buffer.byteLength(raw) <= 32768);
  const req = JSON.parse(raw);
  exact(req, ['op', 'persistDir', 'chatId'].concat(req.op === 'add' ? ['input'] : req.op === 'query' ? ['query', 'topN', 'threshold'] : []));
  assert(['add', 'query', 'list'].includes(req.op));
  assert(/^customer:CUST-\d{3,}$/.test(req.chatId));
  text(req.persistDir, 4096);
  const mod = await import(pathToFileURL(process.env.HMEM_REFERENCE_SRC!).href);
  const hmem = new mod.HMEM({ persistDir: req.persistDir, actor: 'dispute-memory-adapter' });
  const all = hmem.store.all();
  assert(all.length <= 100);
  for (const m of all) {
    assert(m.chatId === req.chatId && Array.isArray(m.tags) && m.tags.includes(req.chatId));
    text(m.source, 200);
    text(m.content, 8192);
  }
  let output;
  if (req.op === 'add') {
    const input = req.input;
    exact(input, inputFields);
    text(input.content, 8192);
    text(input.source, 200);
    assert(/^(decision|unverified-note):[0-9a-f-]{36}$/.test(input.source));
    assert(input.type === 'factual' && input.layer === 'working' && input.confidence === 1);
    assert(input.chatId === req.chatId && Array.isArray(input.tags) && input.tags.length <= 12);
    for (const tag of input.tags) text(tag, 200);
    assert(input.tags.includes(req.chatId));
    exact(input.provenance, ['origin', 'learnedAt', 'label', 'refs']);
    assert(input.provenance.origin === 'plan_completion' || input.provenance.origin === 'manual');
    assert(Number.isSafeInteger(input.provenance.learnedAt) && input.provenance.learnedAt > 0);
    text(input.provenance.label, 200);
    assert(Array.isArray(input.provenance.refs) && input.provenance.refs.length <= 8);
    for (const ref of input.provenance.refs) text(ref, 200);
    const matches = all.filter((m: any) => m.source === input.source);
    assert(matches.length <= 1);
    if (matches.length) {
      const m = matches[0];
      for (const key of inputFields) assert(JSON.stringify(m[key]) === JSON.stringify(input[key]));
      output = { ok: true, memory: publicMemory(m), storage_status: 'reused' };
    } else {
      assert(all.length < 100);
      output = { ok: true, memory: publicMemory(hmem.add(input)), storage_status: 'stored' };
    }
  } else if (req.op === 'query') {
    text(req.query, 2048);
    assert(Number.isInteger(req.topN) && req.topN > 0 && req.topN <= 20);
    assert(Number.isFinite(req.threshold) && req.threshold >= 0 && req.threshold <= 1);
    const result = hmem.query(req.query, { chatId: req.chatId, topN: req.topN, threshold: req.threshold });
    output = { ok: true, memories: result.memories.map((r: any) => publicMemory(r.memory)) };
  } else {
    output = { ok: true, memories: all.map(publicMemory) };
  }
  // Query touches records without persisting; flush those audit changes too.
  hmem.store.persist();
  const ledger = req.persistDir + '/ledger.jsonl';
  if (!fs.existsSync(ledger)) fs.writeFileSync(ledger, '');
  process.stdout.write(JSON.stringify(output) + '\n');
}
main().catch(() => { process.stderr.write('memory_reference_failed\n'); process.exitCode = 1; });
