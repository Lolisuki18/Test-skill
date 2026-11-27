import { parseCents } from "./money.mjs";

export const VALID_STATUSES = ["draft", "submitted", "approved", "rejected"];
export const ALLOWED_TRANSITIONS = {
  draft: ["submitted"],
  submitted: ["approved", "rejected"],
  approved: [],
  rejected: [],
};

export function createLedgerStore() {
  let nextId = 1;
  const items = [];

  function list(status = null) {
    if (status !== null && !VALID_STATUSES.includes(status)) {
      throw new Error(`Invalid status: ${status}`);
    }
    return status === null ? [...items] : items.filter((i) => i.status === status);
  }

  function create({ title, amountCents, ownerId }) {
    if (typeof title !== "string" || title.trim().length === 0 || title.trim().length > 120) {
      throw new Error("title must be a non-empty string <= 120 chars");
    }
    const cents = parseCents(amountCents);
    const entry = {
      id: nextId++,
      title: title.trim(),
      amountCents: cents,
      status: "draft",
      ownerId,
      decidedBy: null,
    };
    items.push(entry);
    return { ...entry };
  }

  function submit(id, actor) {
    const entry = items.find((i) => i.id === id);
    if (!entry) return null;
    if (entry.ownerId !== actor.id && actor.role !== "admin") {
      const err = new Error("Only owner or admin can submit");
      err.code = "FORBIDDEN";
      throw err;
    }
    if (!ALLOWED_TRANSITIONS[entry.status].includes("submitted")) {
      throw new Error(`Cannot transition ${entry.status} -> submitted`);
    }
    entry.status = "submitted";
    return { ...entry };
  }

  function decide(id, decision, actor) {
    if (actor.role !== "admin") {
      const err = new Error("Only admin can approve or reject");
      err.code = "FORBIDDEN";
      throw err;
    }
    if (decision !== "approved" && decision !== "rejected") {
      throw new Error("decision must be approved or rejected");
    }
    const entry = items.find((i) => i.id === id);
    if (!entry) return null;
    if (!ALLOWED_TRANSITIONS[entry.status].includes(decision)) {
      throw new Error(`Cannot transition ${entry.status} -> ${decision}`);
    }
    entry.status = decision;
    entry.decidedBy = actor.id;
    return { ...entry };
  }

  return { list, create, submit, decide };
}
