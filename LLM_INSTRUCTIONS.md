# Global LLM Instructions

This file contains universal instructions for all AI models (Jules, Claude, Gemini, GPT, etc.) working on this project.

## Core Directives
- **Do NOT `taskkill` all node processes.** This will kill your own session and others.
- Always use memory tools at the beginning and end of each session.
- Update all documentation (AGENTS.md, VISION.md, MEMORY.md, ROADMAP.md, TODO.md, CHANGELOG.md, HANDOFF.md) in comprehensive detail at the end of each session.
- Follow the versioning and changelog protocol for every build/major change.

## Versioning & Changelog Protocol
- Every significant build or feature implementation MUST increment the version number.
- The version number is centrally located in `VERSION.md`.
- All other references to the version number in the project must be synchronized with `VERSION.md`.
- Update `CHANGELOG.md` with every version bump.
- When a version is updated, the git commit message MUST reference the new version number.

## Coding Conventions
- Comment your code in depth:
    - What it's doing.
    - Why it's there.
    - Why it's the way it is.
    - Relevant analysis, findings, side effects, bugs, optimizations.
    - Alternate or non-working methods tried.
- Do not comment if it is self-explanatory.
- If existing code lacks necessary comments, add them.

## Session Protocols
### At the beginning of each session/task/turn:
1. Use memory tools.
2. Read all rule documentation (`AGENTS.md`, `LLM_INSTRUCTIONS.md`).
3. Learn repo structure and all documentation.

### At the end of each session/task/turn:
1. Use memory tools.
2. Update all rule and project documentation in comprehensive detail.
3. Update `HANDOFF.md`.
4. Perform a git commit and push.

## Project Structure & Submodules
- Maintain documentation of all submodules with their URLs, descriptions, versions, dates, and build numbers.
- Document the project directory structure and code structure.
- List all libraries with versions and locations, and how they are used.
