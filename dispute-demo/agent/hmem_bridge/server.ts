#!/usr/bin/env node
// Python-to-TypeScript adapter. Imports the official H-MEM engine; does not reimplement it.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

type AddInput = {
  content: string;
  type?: string;
  layer?: string;
  tags?: string[];
  confidence?: number;
  source: string;
  provenance?: {
    origin: string;
    learnedAt: number;
    label: string;
    refs?: string[];
  };
  chatId?: string;
  missionId?: string;
  goalRunId?: string;
};

type Request = {
  op: "add" | "query" | "list";
  persistDir: string;
  actor?: string;
  input?: AddInput;
  query?: string;
  chatId?: string;
  topN?: number;
  threshold?: number;
};

function publicMemory(m: Record<string, unknown>): Record<string, unknown> {
  const { embedding: _embedding, ...rest } = m;
  return rest;
}

function resolveHmemIndex(): string {
  if (process.env.HMEM_REFERENCE_SRC) return process.env.HMEM_REFERENCE_SRC;
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "../../../../hmem-reference/reference/src/index.ts");
}

async function main(): Promise<void> {
  const raw = fs.readFileSync(0, "utf-8");
  const req = JSON.parse(raw) as Request;
  if (!req.persistDir || req.persistDir.trim() === "") {
    throw new Error("persistDir is required");
  }
  const indexPath = resolveHmemIndex();
  const mod = await import(pathToFileURL(indexPath).href);
  const hmem = new mod.HMEM({ persistDir: req.persistDir, actor: req.actor ?? "dispute-agent" });

  if (req.op === "add") {
    if (!req.input) throw new Error("add requires input");
    const record = hmem.add(req.input);
    process.stdout.write(JSON.stringify({ ok: true, memory: publicMemory(record) }) + "\n");
    return;
  }
  if (req.op === "query") {
    if (!req.query) throw new Error("query requires query text");
    const result = hmem.query(req.query, {
      chatId: req.chatId,
      topN: req.topN,
      threshold: req.threshold,
    });
    process.stdout.write(
      JSON.stringify({
        ok: true,
        result: {
          context: result.context,
          trace: result.trace,
          memories: result.memories.map((item: { memory: Record<string, unknown>; relevance: number }) => ({
            relevance: item.relevance,
            memory: publicMemory(item.memory),
          })),
        },
      }) + "\n"
    );
    return;
  }
  if (req.op === "list") {
    const memories = hmem.store.all().map((m: Record<string, unknown>) => publicMemory(m));
    process.stdout.write(JSON.stringify({ ok: true, memories }) + "\n");
    return;
  }
  throw new Error(`unsupported op: ${req.op}`);
}

main().catch((err: unknown) => {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(message + "\n");
  process.stdout.write(JSON.stringify({ ok: false, error: message }) + "\n");
  process.exit(1);
});
