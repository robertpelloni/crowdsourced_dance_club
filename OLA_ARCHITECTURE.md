# Hardware Integration & Open Lighting Architecture (OLA)

## Overview
This document outlines the strategy for decoupling the synchronous hardware control from the core audio thread in the C++ engine.

## Current State
The C++ engine (`engine/src/dmx_controller.cpp`) currently uses blocking `libftdi` USB calls to control DMX lighting based on audio peaks. This risks buffer underruns in the high-priority audio callback.

## Proposed Architecture: OLA Proxy
1. **Decoupling:** Strip `libftdi` from the core audio engine.
2. **Protocol:** The C++ engine will emit lighting commands (e.g., sequences like "strobe_fast" and intensities) over a lightweight UDP socket or WebSocket.
3. **Proxy Daemon:** A standalone Python or C++ daemon will run the Open Lighting Architecture (OLA). It will listen for UDP packets and translate them into native DMX commands for the connected USB hardware.
4. **Benefits:**
   - Prevents audio thread blocking.
   - Allows network-distributed lighting control (the lighting rig doesn't need to be plugged into the same machine as the audio engine).
   - OLA supports a vast array of protocols (Art-Net, sACN, USB DMX), greatly expanding hardware compatibility beyond `libftdi`.

## Next Steps
- Remove `libftdi` dependencies from `CMakeLists.txt` or `Makefile` for the core engine.
- Implement UDP broadcast in `dmx_controller.cpp`.
- Build the `ola_proxy.py` script.
