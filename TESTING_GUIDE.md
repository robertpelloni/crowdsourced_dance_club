# User Testing & Feedback Protocol: Vibe-Check Sessions

This guide outlines a structured protocol for gathering audience feedback to refine the CDC "Cybernetic DJ" algorithms.

## Session Goals
1. Validate algorithmic track transitions under live club conditions.
2. Gather qualitative data on "vibe accuracy" vs. "technical smoothness".
3. Identify edge cases where the Conductor's energy trends drift from crowd sentiment.

---

## 📋 Test Procedure

### 1. Pre-Session Setup
- Deploy the latest Production Gold candidate using `./deploy_production.sh`.
- Ensure at least 5 distinct mobile clients are connected.
- Seed the `tracks` table with a diverse range of genres (Psytrance, Techno, Ambient).

### 2. Live Interaction (The "Dance Phase")
- **Phase A (Algorithmic Control):** Allow the Conductor to select tracks autonomously for 30 minutes. Users should vote for upcoming tracks without manual admin intervention.
- **Phase B (Stress Testing):** Admins should trigger "Energy Peaks" via the dashboard to observe the HPF sweeps and BPM ramping response.

### 3. Feedback Collection (The "Refine Phase")
- Participants are required to use the **Refine** tab in the mobile app.
- **Vibe Accuracy (1-5):** Did the next track feel like a logical musical progression?
- **Technical Smoothness (1-5):** Were there any audible glitches, clicks, or awkward silence during the crossfade?
- **Comments:** Provide context on specific transitions (e.g., "The swap from Techno to Ambient was too abrupt").

---

## 📊 Analytics Audit
After the session, administrators should:
1. Access `/api/admin/analytics/vibe-report` to see aggregated genre success metrics.
2. Review the `feedback` table for specific qualitative pointers.
3. Compare `vibe_score` against the `success_metric` (voting velocity) to identify high-performing "vibe anchors".

## 🚀 Iteration Strategy
Use the findings to adjust `CONFIG` weights in `src/core/conductor.py`:
- If Vibe Accuracy is low: Increase `VIBE_WEIGHT_KEY` or `VIBE_WEIGHT_GENRE`.
- If Technical Smoothness is low: Increase `crossfade_duration` in the Conductor's `TRACK_SYNC` payload.
