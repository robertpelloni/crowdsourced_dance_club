# CrowdClub User Testing Guide (v2.2.0)

## Overview
This guide provides instructions for validating the 'Cybernetic Intelligence' release candidate. Testing is divided into three personas: Venue Admin, Registered Member, and Guest.

## Environment Setup
1. Ensure the Conductor Server is running: `python src/main.py`
2. Ensure the Audio Engine is active: `./engine/cdc_engine`
3. Launch the Mobile Client or Web Prototype.

## Persona 1: Venue Admin
**Goal:** Manage the room and optimize the AI.
1. **Login:** Authenticate using admin credentials.
2. **ML Retraining:** Navigate to the Admin Dashboard and trigger a 'Model Retrain'. Verify status changes to 'READY'.
3. **Analytics Audit:** View the 'Vibe Report' and ensure user impact metrics are populating.
4. **Manual Override:** Execute an 'ADMIN_SKIP' to verify immediate audio engine response.

## Persona 2: Registered Member
**Goal:** Engage with the vibe and earn points.
1. **Registration/Referral:** Create a new account using a referral code. Verify both users receive +50 points.
2. **Requesting:** Request a song. Verify it appears in the queue after the 'Algorithmic Vibe Check'.
3. **Voting:** Upvote an upcoming track. Verify the queue re-sorts based on the weighted vibe/vote algorithm.
4. **Feedback:** At the end of a track, submit a 'Vibe Rating' (1-5 stars).

## Persona 3: Guest (Anonymous)
**Goal:** Low-friction interaction.
1. **Sync:** Scan the venue QR code to connect.
2. **Vibe Check:** Request a track that clashes with the current BPM (e.g., 145 BPM vs 100 BPM). Verify 'REQUEST_DENIED' with a clear reason.

## Success Criteria
- 100% of 'Perfect Matches' are accepted.
- Audio Engine crossfades trigger precisely at the Conductor's timestamp.
- ML Model updates influence transition archetype selection within 2 cycles.
