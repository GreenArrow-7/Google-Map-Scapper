# CLAUDE.md — Google Maps Scraper Kit

You are working inside the **Google Maps Scraper Kit**. This folder runs a local Google Maps scraper
and you drive it for the user.

## What this project is
A Docker-based local deployment of the open-source `gosom/google-maps-scraper`, exposed as a REST API
at **`http://localhost:8080`**, plus a skill that teaches you to use it. It scrapes **Google Maps
business listings only** (not social media).

## When the user asks to scrape businesses / get a list of places / lead-gen data
**Load and follow the `google-maps-scraper` skill** (`.claude/skills/google-maps-scraper/SKILL.md`).
It has the exact API flow, the required fields, and the best-practice + safety rules. Don't improvise
the API calls from memory — use the skill.

## Slash commands
This kit ships commands in `.claude/commands/` that map to the skill: `/scrape` (single query),
`/scrape-batch` (many queries, one job), `/scrape-setup` (start the scraper), `/scrape-jobs` (list/delete).
Local commands are pre-approved in `.claude/settings.json` so you can run them without prompting the user.

## Rate limits — warn, don't block
If a request is large/high-volume (high `depth`, many keywords, repeated runs, or `email:true`), **proceed**
but first print ONE short warning that over-use can get the user's IP temporarily rate-limited by Google,
and suggest proxies. Do NOT gate or demand confirmation for a normal big scrape. Refuse only clearly
abusive use (surveilling individuals, spam). Full guidance is in the skill.

## Hard facts you must not get wrong
- API base: `http://localhost:8080` — **no auth** (it's localhost-only). Never expose it publicly.
- Create a job: `POST /api/v1/jobs`. **Required** body fields or it 422s:
  `max_time` (in **NANOSECONDS** — seconds × 1e9, e.g. `300000000000` for 300s; a bare `300` is read as
  300 *nanoseconds* and the job is silently capped at the server's 180s minimum), `lat` & `lon`
  (as **strings**), plus `keywords` (array).
- The create response returns `{"id":"<uuid>"}` (lowercase `id`). Status checks use `GET /api/v1/jobs/{id}` whose field is `"Status"` and becomes `"ok"` when done.
- **`"ok"` does not mean complete.** A job that hits its time budget is cancelled and *still* reported
  as `"ok"` with partial results. Time the job; if it ran its whole budget, tell the user the rows are
  incomplete. The scripts warn automatically — never report a row count as final without this check.
- **Poll in the background.** The Bash tool blocks foreground `sleep`; run the poll loop as a
  background command (`run_in_background: true`) and read its output file when notified.
- Before a big job (high depth / many keywords), **warn once and proceed** — see "Rate limits" above.
  Do not gate it behind a confirmation; that contradicts the warn-don't-block rule.
- Scraped emails/phones are **personal data**; don't dump huge CSVs into chat — summarize + save to disk.

## Setup
If the container isn't running: `docker compose up -d`, then verify `curl http://localhost:8080/api/v1/jobs`.
Full setup is in `SETUP.md`.

## Attribution
This wraps `gosom/google-maps-scraper` (MIT, © Georgios Komninos). Keep `CREDITS.md` + `LICENSE` intact.
