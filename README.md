# Crowdsourced Dance Club

Welcome to the **Crowdsourced Dance Club (CDC)**. A cybernetic, globally scalable, and ML-driven approach to real-time algorithmic DJing.

The system leverages a complex 3-tiered architecture (React Native -> Python FastAPI -> C++ PortAudio Engine) to build "The Sentient Venue".

## Current State: [v3.4.0]
Phase 1, Phase 2, Phase 3, and **Phase 4** are officially complete and successfully tested via Playwright and Locust.

### Notable Features:
*   **Neural Conductor:** Uses `scikit-learn` Random Forest to predict track vibe transitions organically from database history.
*   **Multi-Agent DJ Battles:** AI Personas fight for deck control.
*   **Generative Immersion:** Natively extracts audio features in the C++ layer, broadcasting via WebSockets to drive a Three.js WebXR Vibe Orb and stable diffusion visuals.
*   **Decentralized Governance:** Full CRUD routing for CDC DAO macro-rule proposals.
*   **Biometric Sync:** Ingests WearOS heart-rate data to physically trigger peak energy states.
*   **Stem Mixing & Virtual MCs:** Real-time 4-stem C++ mixing using Demucs. Generative gTTS hype tracking.

Please review `HANDOFF.md` and `PROJECT_MEMORY.md` for specific architectural design choices made during development.
