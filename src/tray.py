#!/usr/bin/env python3
"""
CDC System Tray Icon & Server Process Controller
Provides desktop system tray access to:
 - Conductor server status & health
 - Launching Web Dashboard
 - Launching 3D Vibe Orb WebXR visualizer
 - Live log tailing
 - Graceful server termination / restart
 - Headless CLI fallback when no X11/GUI display is available.
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
import threading
from typing import Optional

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"
VIBE_ORB_URL = f"{SERVER_URL}/static/vibe_orb.html"
LOG_FILE = "conductor.log"

server_proc: Optional[subprocess.Popen] = None

def get_server_status() -> str:
    """Checks if the Conductor server is actively listening on port 8000."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex((HOST, PORT)) == 0:
            return "RUNNING"
    return "STOPPED"

def start_server():
    """Starts the uvicorn Conductor backend process."""
    global server_proc
    if get_server_status() == "RUNNING":
        print("[TRAY] Conductor is already running.")
        return
    print(f"[TRAY] Starting Conductor on {SERVER_URL}...")
    log_fd = open(LOG_FILE, "a")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", HOST, "--port", str(PORT)],
        stdout=log_fd,
        stderr=subprocess.STDOUT
    )
    time.sleep(1.0)
    print(f"[TRAY] Conductor process PID: {server_proc.pid}")

def stop_server():
    """Stops the Conductor backend process and any matching uvicorn processes."""
    global server_proc
    print("[TRAY] Stopping Conductor servers...")
    if server_proc and server_proc.poll() is None:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        server_proc = None

    # Clean up any lingering process on port 8000
    try:
        res = subprocess.check_output(f"lsof -t -i :{PORT}", shell=True).decode().strip()
        for pid in res.splitlines():
            if pid.strip():
                os.kill(int(pid.strip()), signal.SIGTERM)
                print(f"[TRAY] Killed PID {pid} on port {PORT}")
    except Exception:
        pass
    print("[TRAY] Conductor servers stopped.")

def restart_server():
    stop_server()
    time.sleep(0.5)
    start_server()

def open_dashboard():
    print(f"[TRAY] Opening Dashboard: {SERVER_URL}")
    webbrowser.open(SERVER_URL)

def open_vibe_orb():
    print(f"[TRAY] Opening Vibe Orb: {VIBE_ORB_URL}")
    webbrowser.open(VIBE_ORB_URL)

def tail_logs(lines: int = 25):
    """Prints recent log lines to stdout."""
    if not os.path.exists(LOG_FILE):
        print("[TRAY] No log file exists yet.")
        return
    print(f"\n--- Recent Logs ({LOG_FILE}) ---")
    with open(LOG_FILE, "r") as f:
        all_lines = f.readlines()
        for l in all_lines[-lines:]:
            print(l.rstrip())
    print("--- End Logs ---\n")

def run_headless_cli():
    """Interactive command-line control when no desktop/display server is found."""
    print("======================================================")
    print("  Crowdsourced Dance Club - System Controller (CLI)   ")
    print("======================================================")
    print(f"Status: {get_server_status()}")
    print("Commands:")
    print("  [s] Start Conductor Server")
    print("  [k] Stop / Kill Server")
    print("  [r] Restart Server")
    print("  [d] Open Dashboard URL")
    print("  [v] Open 3D Vibe Orb URL")
    print("  [l] View Recent Logs")
    print("  [q] Quit Controller")
    print("======================================================")

    if not sys.stdin.isatty():
        print("[TRAY] Non-interactive environment detected. Executing status probe.")
        print(f"[TRAY] Conductor status: {get_server_status()}")
        return

    while True:
        try:
            cmd = input("CDC-Tray> ").strip().lower()
            if cmd == 's':
                start_server()
            elif cmd == 'k':
                stop_server()
            elif cmd == 'r':
                restart_server()
            elif cmd == 'd':
                open_dashboard()
            elif cmd == 'v':
                open_vibe_orb()
            elif cmd == 'l':
                tail_logs()
            elif cmd == 'q' or cmd == 'exit':
                print("[TRAY] Exiting.")
                break
            else:
                print("Unknown command. Valid options: s, k, r, d, v, l, q")
        except (KeyboardInterrupt, EOFError):
            print("\n[TRAY] Exiting.")
            break

def create_tray_image():
    """Creates a 64x64 neon club icon for the system tray."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw neon green disco circle
    draw.ellipse([4, 4, 60, 60], fill=(15, 15, 15), outline=(0, 255, 128), width=3)
    # Draw stylized soundwave / CDC initials
    draw.line([16, 32, 24, 18], fill=(0, 255, 128), width=3)
    draw.line([24, 18, 32, 46], fill=(0, 255, 128), width=3)
    draw.line([32, 46, 40, 22], fill=(0, 255, 128), width=3)
    draw.line([40, 22, 48, 32], fill=(0, 255, 128), width=3)
    return img

def run_tray():
    """Initializes the GUI tray icon using pystray, falling back to CLI if headless."""
    display = os.getenv("DISPLAY")
    if not display:
        print("[TRAY] No DISPLAY detected. Running in headless CLI mode.")
        run_headless_cli()
        return

    try:
        import pystray
        from pystray import MenuItem as item

        icon_image = create_tray_image()

        def on_open_dashboard(icon, item):
            open_dashboard()

        def on_open_orb(icon, item):
            open_vibe_orb()

        def on_start(icon, item):
            start_server()

        def on_restart(icon, item):
            restart_server()

        def on_stop(icon, item):
            stop_server()

        def on_exit(icon, item):
            stop_server()
            icon.stop()

        menu = pystray.Menu(
            item('CDC Conductor Status: ' + get_server_status(), lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Open Dashboard UI', on_open_dashboard),
            item('Open 3D Vibe Orb', on_open_orb),
            pystray.Menu.SEPARATOR,
            item('Start Conductor Server', on_start),
            item('Restart Conductor Server', on_restart),
            item('Stop Conductor Server', on_stop),
            pystray.Menu.SEPARATOR,
            item('Quit Tray & Stop Servers', on_exit)
        )

        tray_icon = pystray.Icon("CDC_Conductor", icon_image, "CDC AI Conductor", menu)
        print("[TRAY] Running desktop system tray icon...")
        tray_icon.run()

    except Exception as e:
        print(f"[TRAY] Unable to initialize GUI tray ({e}). Falling back to CLI mode.")
        run_headless_cli()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "start":
            start_server()
        elif arg == "stop":
            stop_server()
        elif arg == "restart":
            restart_server()
        elif arg == "status":
            print(f"Server status: {get_server_status()}")
        elif arg == "cli":
            run_headless_cli()
        else:
            print("Usage: python3 src/tray.py [start|stop|restart|status|cli]")
    else:
        run_tray()
