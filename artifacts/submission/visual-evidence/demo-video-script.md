# Demo Video Script — AfrekaOS Offline (Task 005B)

> Plain narration for a 2–3 minute demo video.
> Direct and honest. Pair with `demo-video-shot-list.md` (the shot plan).

---

**[0:00 — Mission Control]**

AfrekaOS Offline is a local SME operations copilot for African business
operators. Everything you're about to see runs locally — on the operator's own
machine. There is no cloud model, no cloud database, and no external API.

**[0:15 — Why local]**

Power and connectivity are intermittent. Records are often informal. So the
copilot runs entirely on a low-cost laptop, offline, served through a browser on
localhost.

**[0:30 — How it works]**

It uses a local Qwen GGUF model — qwen3-1.7b in direct-answer mode. The
operator's question is matched against local SME operations notes using SQLite
FTS5 retrieval, and the top results are injected as context before the model
answers. That keeps the guidance grounded.

**[0:45 — Demo scenario]**

Here's a demo scenario — low sales, two fast-moving items out of stock, a
delayed supplier delivery, and more customers asking for credit. This is a demo
prompt only — no private business data.

**[1:10 — Daily Operations Advisor result]**

The Daily Operations Advisor returns a short operating checklist — practical
steps for stockouts, supplier delays, and credit pressure, grounded in the
retrieved notes.

**[1:35 — Inventory and Cashflow]**

There are focused advisors for inventory and stock checks, and for cashflow
pressure. Each gives operating checklists for everyday situations.

**[1:50 — Offline System Status]**

The status page confirms what's running: the locked local model, the SQLite
retrieval index, and the no-cloud-dependency statement.

**[2:15 — Boundaries]**

AfrekaOS provides operational guidance only. It is not accounting, banking,
payroll, tax, lending, or ERP software. Operators should verify their own
records before acting.

**[2:30 — Honest status]**

One open item: this package has not yet passed a true Ubuntu 22.04 / 8 GB run.
That target-hardware risk remains open. The local-only, offline thesis holds —
but final target validation is still pending.

---

## Notes for the narrator

- Keep it direct and honest. Do not overclaim.
- Use demo prompts only. Do not show private or customer data.
- If the on-device run is slow, that is fine — let it be visible rather than
  editing it out.
