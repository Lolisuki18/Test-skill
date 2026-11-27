import http from "node:http";
import { pathToFileURL } from "node:url";
import { formatUsd } from "./money.mjs";
import { createLedgerStore } from "./store.mjs";

const MAX_BODY = 32 * 1024;
const DEMO_USERS = {
  "admin-token": { id: "u-admin", role: "admin" },
  "member-token": { id: "u-member", role: "member" },
};

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function sendJson(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;
    req.on("data", (c) => {
      total += c.length;
      if (total > MAX_BODY) {
        reject(new Error("Payload too large"));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on("end", () => {
      try {
        const parsed = JSON.parse(Buffer.concat(chunks).toString("utf-8"));
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
          reject(new Error("JSON body must be an object"));
          return;
        }
        resolve(parsed);
      } catch {
        reject(new Error("Invalid JSON"));
      }
    });
    req.on("error", reject);
  });
}

function requireActor(req, res) {
  const auth = req.headers.authorization || "";
  if (!auth.startsWith("Bearer ")) {
    sendJson(res, 401, { error: "authentication required" });
    return null;
  }
  const actor = DEMO_USERS[auth.slice(7).trim()];
  if (!actor) {
    sendJson(res, 401, { error: "invalid token" });
    return null;
  }
  return actor;
}

export function createLedgerServer(store = createLedgerStore()) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url || "/", "http://127.0.0.1");
    if (req.method === "GET" && url.pathname === "/health") {
      sendJson(res, 200, { status: "ok", runtime: "node" });
      return;
    }
    if (req.method === "GET" && url.pathname === "/") {
      const rows = store
        .list()
        .map((e) => `<li><strong>${escapeHtml(e.title)}</strong> (${formatUsd(e.amountCents)}) — <em>${e.status}</em></li>`)
        .join("\n");
      const html = `<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Ledger Node</title></head><body><main><h1>Expense Ledger</h1><ul>${rows || "<li>No expenses</li>"}</ul></main></body></html>`;
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Content-Length": Buffer.byteLength(html) });
      res.end(html);
      return;
    }
    if (req.method === "GET" && url.pathname === "/api/expenses") {
      const status = url.searchParams.get("status");
      try {
        sendJson(res, 200, { expenses: store.list(status) });
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }
    if (req.method === "POST" && url.pathname === "/api/expenses") {
      const actor = requireActor(req, res);
      if (!actor) return;
      try {
        const body = await readJson(req);
        const created = store.create({
          title: body.title,
          amountCents: body.amountCents,
          ownerId: actor.id,
        });
        sendJson(res, 201, { expense: created });
      } catch (err) {
        sendJson(res, 400, { error: err.message });
      }
      return;
    }
    const submitMatch = url.pathname.match(/^\/api\/expenses\/(\d+)\/submit$/);
    if (req.method === "PATCH" && submitMatch) {
      const actor = requireActor(req, res);
      if (!actor) return;
      try {
        const updated = store.submit(Number(submitMatch[1]), actor);
        if (!updated) {
          sendJson(res, 404, { error: "not found" });
          return;
        }
        sendJson(res, 200, { expense: updated });
      } catch (err) {
        sendJson(res, err.code === "FORBIDDEN" ? 403 : 400, { error: err.message });
      }
      return;
    }
    const decideMatch = url.pathname.match(/^\/api\/expenses\/(\d+)\/decide$/);
    if (req.method === "PATCH" && decideMatch) {
      const actor = requireActor(req, res);
      if (!actor) return;
      try {
        const body = await readJson(req);
        const updated = store.decide(Number(decideMatch[1]), body.decision, actor);
        if (!updated) {
          sendJson(res, 404, { error: "not found" });
          return;
        }
        sendJson(res, 200, { expense: updated });
      } catch (err) {
        sendJson(res, err.code === "FORBIDDEN" ? 403 : 400, { error: err.message });
      }
      return;
    }
    sendJson(res, 404, { error: "not found" });
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT || 8098);
  createLedgerServer().listen(port, "127.0.0.1");
}
