#!/usr/bin/env python3
"""Self-check for the max_time unit fix. Runs offline: python scripts/test_scrape.py"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape

def go_duration_seconds(json_number):
    """What the server sees: Go unmarshals a JSON number into time.Duration as
    NANOSECONDS, then webrunner.go clamps anything under 180s up to 180s."""
    secs = json_number / 1e9
    return 180 if secs < 180 else secs

# The bug this guards: sending plain seconds gave every job the same 180s floor.
assert go_duration_seconds(600) == 180, "plain seconds must NOT reach the server"
assert go_duration_seconds(900) == 180
assert go_duration_seconds(600 * scrape.NS) == 600, "nanoseconds must survive the round trip"
assert go_duration_seconds(1800 * scrape.NS) == 1800

# The job body must carry the conversion.
src = io.open(os.path.join(os.path.dirname(__file__), "scrape.py"), encoding="utf-8").read()
assert '"max_time": a.max_time * NS' in src, "max_time conversion was dropped from the job body"

# effective_timeout mirrors the server's 180s floor.
assert scrape.effective_timeout(60) == 180
assert scrape.effective_timeout(180) == 180
assert scrape.effective_timeout(600) == 600

# looks_truncated: a job that burns its whole budget is reported "ok" but is partial.
assert scrape.looks_truncated(600, 600) is True, "ran to deadline -> truncated"
assert scrape.looks_truncated(590, 600) is True, "within slack of deadline -> truncated"
assert scrape.looks_truncated(120, 600) is False, "finished early -> complete"
assert scrape.looks_truncated(180, 60) is True, "short budget still floors at 180"
assert scrape.looks_truncated(20, 60) is False

print("ok - max_time is sent in nanoseconds and truncation is detected")
