# Global Network: Decentralized Venue Sync Protocol

## Overview
As part of Milestone 4 (Scaling & Expansion), the Crowdsourced Dance Club (CDC) aims to support a global network of synchronized venues. This document outlines the proposed decentralized venue sync protocol.

## Objective
To allow multiple independent instances (venues) of the CDC to share states, enabling global leaderboard aggregations, "DJ Battles" between venues, and seamless cross-venue user roaming without a single central bottleneck.

## Proposed Protocol: WebRTC Data Channels
Instead of relying on a centralized monolithic database server, we will implement a decentralized mesh using WebRTC.

### Why WebRTC?
1. **Low Latency:** WebRTC's UDP-based data channels provide ultra-low latency for state synchronization (crucial for live DJ events).
2. **Peer-to-Peer:** Reduces server bandwidth costs; venues sync directly with each other.
3. **NAT Traversal:** Built-in STUN/TURN support handles complex venue network topologies.

### Sync Mechanisms
1. **Signaling Server:** A lightweight, central WebSocket server (e.g., in Python/FastAPI) will act only as a signaling tracker, helping venues discover each other and exchange WebRTC SDP offers/answers.
2. **State Gossip:** Once connected via WebRTC, venues will use a gossip protocol to broadcast lightweight state diffs (e.g., current playing track ID, local voting velocity, venue aggregate vibe score).
3. **Conflict Resolution:** We will utilize CRDTs (Conflict-free Replicated Data Types) for global leaderboards and user point aggregates to ensure eventual consistency without distributed locking.

## Next Steps
- Implement the signaling hub in the existing FastAPI application.
- Integrate `aiortc` (Python WebRTC library) into the Conductor to manage peer connections.
- Define the CRDT structures for shared global state.
