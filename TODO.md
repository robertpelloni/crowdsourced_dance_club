# TODO List

## Immediate Tasks (Phase 4 Initialization)
- [x] Research and initialize a new microservice architecture in `src/telemetry/` for high-frequency biometric data ingestion.
- [ ] Investigate `fastapi-websocket` optimizations or alternative pub/sub brokers (e.g., Redis or NATS) to handle extreme WebSocket load for telemetry data.
- [x] Define the GraphQL schema or REST endpoints required for the WearOS / Apple Watch companion apps.
- [x] Audit the `engine/` C++ DSP chain to extract feature arrays (RMS, transient peaks per stem) and expose them via UDP or websockets to feed into the future ComfyUI Generative Video node.
- [x] Set up a staging environment for the "Vibe Orb" WebXR visualization (explore Three.js / React Three Fiber integrations within the current frontend).
- [ ] Initialize the Generative Video Synthesis framework to bridge Conductor state to ComfyUI/Stable Diffusion nodes.

## Backlog / Technical Debt
- [ ] Evaluate porting the core `evaluate_track_fit` Random Forest logic to a faster, compiled language (like Rust) if multi-agent concurrent evaluation becomes a bottleneck.
- [ ] Clean up redundant `spleeter` installation artifacts from early testing, ensuring only `demucs` dependencies are referenced in `requirements.txt`.
- [ ] Expand the automated test suite to include load testing scripts (e.g., Locust) targeting the new multi-tenant `venue_states` dictionary under extreme concurrent voting conditions.
