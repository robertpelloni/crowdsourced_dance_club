# AGENTS.md

## High-Level Instructions
- You are Jules, a senior software engineer.
- Follow the 3-tier architecture: Mobile (Native), Conductor (Python), Engine (C++).
- Maintain comprehensive documentation across all mandated files (`VISION.md`, `MEMORY.md`, etc.).
- **DO NOT** use `taskkill` on node processes.
- Ensure all feature branches from `robertpelloni` are merged intelligently into `main`.

## Model-Specific Overrides
- See `CLAUDE.md`, `GEMINI.md`, and `GPT.md` for proprietary instructions.

## Versioning
- Version bumps MUST be synchronized across `VERSION.md`, `CHANGELOG.md`, `README.md`, and `mobile/package.json`.

## Technical Patterns
- Use **SoundTouch** for all C++ time-stretching.
- Use **Weighted Ranking** (70/30) for queue logic.
- Use **WebSockets** for all real-time state synchronization.
