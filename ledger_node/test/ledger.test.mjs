import assert from "node:assert/strict";
import test from "node:test";
import { formatUsd } from "../src/money.mjs";
import { createLedgerServer } from "../src/server.mjs";

test("money formatting uses integer cents", () => {
  assert.equal(formatUsd(1250), "$12.50");
  assert.equal(formatUsd(5), "$0.05");
});

test("HTTP RBAC, state transitions, and XSS escaping", async () => {
  const server = createLedgerServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  const base = `http://127.0.0.1:${port}`;

  try {
    const h = await fetch(`${base}/health`);
    assert.equal(h.status, 200);
    assert.deepEqual(await h.json(), { status: "ok", runtime: "node" });

    // Unauthenticated create -> 401
    const unauth = await fetch(`${base}/api/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Taxi", amountCents: 1500 }),
    });
    assert.equal(unauth.status, 401);

    // Member creates & submits
    const c = await fetch(`${base}/api/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer member-token" },
      body: JSON.stringify({ title: "<script>alert(1)</script>", amountCents: 2599 }),
    });
    assert.equal(c.status, 201);
    const { expense } = await c.json();

    const sub = await fetch(`${base}/api/expenses/${expense.id}/submit`, {
      method: "PATCH",
      headers: { Authorization: "Bearer member-token" },
    });
    assert.equal(sub.status, 200);

    // Member cannot approve -> 403; Admin approves -> 200
    const memDecide = await fetch(`${base}/api/expenses/${expense.id}/decide`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: "Bearer member-token" },
      body: JSON.stringify({ decision: "approved" }),
    });
    assert.equal(memDecide.status, 403);

    const admDecide = await fetch(`${base}/api/expenses/${expense.id}/decide`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: "Bearer admin-token" },
      body: JSON.stringify({ decision: "approved" }),
    });
    assert.equal(admDecide.status, 200);

    const page = await fetch(`${base}/`);
    const html = await page.text();
    assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
    assert.match(html, /\$25\.99/);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
