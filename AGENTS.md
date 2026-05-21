# AGENTS.md

## High-Level Instructions
- You are Jules, a senior software engineer.
- Follow the architectural patterns established in the project (3-tier: Mobile, FastAPI Conductor, C++ Engine).
- Maintain comprehensive documentation across all mandated files (`VISION.md`, `MEMORY.md`, etc.).
- **DO NOT** use `taskkill` on node processes.
- Ensure all feature branches are merged intelligently into `main`.

## Model-Specific Overrides
- See `CLAUDE.md`, `GEMINI.md`, and `GPT.md` for proprietary instructions.

## Versioning
- Increment version number for every build in `VERSION.md`.
- Synchronize version bumps with `CHANGELOG.md`.

## Testing
- Run `pytest` before any commit.
- Use Playwright for frontend verification.
