# Phase 1 Release Notes

## Summary

This phase-1 submission focuses on closing the core download loop and removing the regressions found during review and browser testing.

## Included Fixes

- Expired tasks are now cleaned before task detail, stable download, and direct download responses are returned.
- The home page now clears stale resolve results when the URL input changes.
- Creating a task now always uses the most recently resolved URL instead of the current textarea value.
- The built-in demo URL now points to `https://samplelib.com/lib/preview/mp4/sample-5s.mp4` so the first-run flow can complete successfully.
- FastAPI shutdown handling now uses lifespan instead of the deprecated `@app.on_event("shutdown")` hook.
- Added `.gitignore` entries for Playwright artifacts and local output folders.

## Validation

Validated on 2026-05-03 with:

- `cd apps/api && python -m pytest`
- `cd apps/web && npm.cmd run test:run`
- `cd apps/web && npm.cmd run build`
- Playwright CLI smoke test covering:
  - demo link fill -> resolve -> create task -> task completion -> stable file download
  - clearing stale resolve state after editing the input URL

## Current Boundaries

- This sample source currently resolves to a stable-download-only flow in phase 1, so direct-download buttons are not guaranteed for that scenario.
- The project still only targets public, non-DRM, non-authenticated content.
