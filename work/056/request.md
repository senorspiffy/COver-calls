# Work item 056
Type: BUG
Scope: FULL
Opened by: I2 (project thread), from a VPS run
Date: 2026-11-12

## What we want
A Webull rate-limit reply (HTTP 429, "Too many requests") waits and retries instead of crashing the scan.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
2026-11-12 on the VPS: the weekly scratch scan, run right after the quality scan, stopped with Webull's "429 Too many requests"; the same command succeeded on a manual retry. `WebullSandboxBroker._call` raised on any non-200 with no retry.
