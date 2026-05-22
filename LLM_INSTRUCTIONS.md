# LLM_INSTRUCTIONS.md

## 🚨 CRITICAL DIRECTIVE: NO TASKKILL
- **NEVER** use `taskkill` or similar commands to terminate all `node` or `python` processes. This will kill your own execution environment and disrupt other active sessions. Use targeted process identification (PIDs) if necessary, but err on the side of caution.

## 🏗️ ARCHITECTURAL MANDATE: THE 3-TIER ECOSYSTEM
This project is built on a strictly decoupled 3-tier real-time architecture:
1.  **Tier 1: Mobile App (React Native / Expo):** High-performance user interface with WebSocket synchronization and haptic beat feedback.
2.  **Tier 2: AI Conductor Server (Python / FastAPI):** The "Brain" of the venue. Manages state, reorders the queue based on "Vibe Fit" (70%) vs Votes (30%), and broadcasts updates via WebSockets.
3.  **Tier 3: Real-Time Audio Engine (C++ / PortAudio):** Low-latency playback loop. Performs real-time time-stretching via SoundTouch and executes precision transitions based on server-side timestamps.
4.  **Utility: auto_dj_script (Python Submodule):** Leveraged for high-fidelity offline renders of master sets or highlight reels.

## 📜 DOCUMENTATION PROTOCOL
Every feature implementation MUST be accompanied by updates to:
- **VISION.md:** Maintain the ultimate design goal and foundational concepts.
- **MEMORY.md:** Record ongoing technical observations, sweet spots (e.g., delta thresholds), and known challenges.
- **ROADMAP.md:** Track major structural milestones.
- **TODO.md:** Maintain a granular list of pending tasks and minor fixes.
- **CHANGELOG.md:** Document every versioned build with "Added", "Fixed", and "Changed" sections.
- **HANDOFF.md:** Prepare a summary for subsequent implementation models.
- **STRUCTURE.md:** Explain the project layout and data flow across all three tiers.
- **LIBRARIES.md:** List all dependencies, versions, and the intelligence behind their selection.

## 🏷️ VERSIONING & COMMITS
- **Single Source of Truth:** The project version is maintained in `VERSION.md`.
- **Sync Rule:** All version bumps MUST be synchronized across `VERSION.md`, `CHANGELOG.md`, `README.md`, and `mobile/package.json`.
- **Commit Format:** Every version bump must be referenced in the git commit message (e.g., `feat: bump version to 0.2.7 and implement ...`).

## 🧪 TESTING & VERIFICATION
- **Python:** Run `pytest tests/` before every submission.
- **C++:** Ensure the engine compiles successfully using the provided `Makefile` in the `engine/` directory.
- **Frontend:** Use visual inspection and Playwright if applicable. Use `expo start` to verify mobile changes if environment allows.

## 🧠 CORE FOUNDATIONAL VISION
The goal is a "collaborative, algorithmic club-night engine" where crowd engagement directly steers the venue vibe. Prioritize user satisfaction, zero-latency feedback, and harmonic flow.
