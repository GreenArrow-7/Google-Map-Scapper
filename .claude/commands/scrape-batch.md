---
description: Scrape many Google Maps queries at once (batch) from a list of keywords
argument-hint: <keywords-file> [--city "City, ST"]
---
The user wants a **batch** Google Maps scrape. Input: **$ARGUMENTS** (a keywords file, optionally a city).

Use the `google-maps-scraper` skill. The API scrapes **many keywords in ONE job** (the `keywords` array),
so batch = one job with all terms.

1. Ensure the scraper is up (`curl -s http://localhost:8080/api/v1/jobs`; `docker compose up -d` if not).
2. Read the keyword list (one per line; ignore blank / `#` lines). If a `--city` was given, geocode it once
   for `lat`/`lon`; otherwise expect the location baked into each keyword (geocode the first one).
3. **ASK about social profiles first** (skip only if the user already said yes/no): *"Also grab social profiles
   (Instagram / Facebook / LinkedIn) for these? Emails are already included. (yes / no)"* — if yes, add `--socials`.
4. **Warn, don't block:** a batch with many keywords is high-volume — print ONE short warning that this can
   get the IP temporarily rate-limited and suggest proxies for large/repeated runs, then **proceed**.
5. POST a single job with the full `keywords` array + required fields (`max_time` in **nanoseconds** —
   seconds × 1e9 — and string `lat`/`lon`) and **`"email": true`** (emails on — the key lead field).
   Use a generous `max_time` (e.g. `900000000000` = 900s) since many keywords + email extraction take
   longer. A bare `900` means 900 *nanoseconds* and the job gets capped at 180s. Poll in the
   BACKGROUND, download. **Then check for truncation:** if the job used its whole budget it was cut
   off mid-scrape and reports `ok` anyway — tell the user the rows are partial.
6. Present results grouped/clean and save the full file to disk.

Tip: `py -3 scripts/scrape.py --keywords-file <file> --city "<City, ST>"` (Windows; `python3` on macOS/Linux) already does all of this — emails are on by
default; append `--socials` if the user said yes in step 3.
