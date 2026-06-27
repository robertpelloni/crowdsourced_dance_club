# OLA (Open Lighting Architecture) & DMX Decoupling Specification

## 1. Problem Statement
Currently, `dmx_controller.cpp` natively binds to `libftdi1` directly inside the core C++ `cdc_engine`.
While functional for single-venue MVP setups (Milestone 5), this tightly couples physical hardware execution to the critical audio DSP loop. If the FTDI USB bus hangs, the audio callback risks a buffer under-run, destroying the time-stretching mix.

## 2. Proposed Architecture
For Phase 5, the lighting controller must be completely decoupled via a Network Proxy.

### The DMX Proxy Microservice
- **Language:** Go or Rust (For extreme low-latency UDP handling without Python's GIL).
- **Function:** Listens on `localhost:9090` via UDP or WebSockets. Translates abstract JSON lighting sequences (e.g., `{"sequence": "strobe_fast"}`) into raw 512-byte DMX arrays.
- **Hardware Interface:** Owns the `libftdi` / OLA daemon connection.

### Core Engine Refactor
- The C++ `AudioEngine` will strip out `#include <ftdi.h>`.
- The `handle_lighting_control` WebSocket callback will instead relay the sequence directly to the DMX Proxy via non-blocking UDP packets.

## 3. Advantages
- **Fault Tolerance:** A crashed lighting board will no longer halt the master audio mix.
- **Scalability:** Venues can run the audio engine on a cloud server and run the DMX Proxy locally on a Raspberry Pi attached to the lighting rig via a secure tunnel.
- **Hardware Agnostic:** By moving towards OLA, we gain support for Art-Net, sACN, and USB-DMX natively, rather than just FTDI chips.
