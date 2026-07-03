# app/

Local browser app on localhost. **Not implemented yet.**

This directory will hold the local server and operator-facing UI in a later
task. Per the scoring discipline, the model and runtime path are locked before
the UI is built. See `../specs/001-afrekaos-offline/plan.md` and
`../SCORING.md`.

Constraints (hard):

- Local-only. No external API or internet dependency during judged runtime.
- Runs on localhost on a low-cost Ubuntu 22.04 laptop, 8 GB RAM, integrated
  graphics.
