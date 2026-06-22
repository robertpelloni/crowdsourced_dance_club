import asyncio
import subprocess
import logging

logger = logging.getLogger("ShadowPilot")

class ShadowPilot:
    """
    A proactive background anomaly detector.
    Monitors git diffs, submodule states, and attempts auto-remediation.
    """
    def __init__(self):
        self.is_active = False
        self.last_anomaly = None
        self.status_msg = "IDLE"
        self.diff_count = 0

    def _run_cmd(self, cmd: str) -> str:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            return result.stdout.strip()
        except Exception as e:
            return str(e)

    def check_git_anomalies(self):
        """Checks for uncommitted changes or submodule detachments."""
        self.status_msg = "EVALUATING"

        diff_output = self._run_cmd("git diff --name-only")
        if diff_output:
            files_changed = len(diff_output.split('\n'))
            self.diff_count = files_changed
            self.last_anomaly = f"Uncommitted changes detected in {files_changed} files."
            logger.warning(f"[ShadowPilot] Anomaly: {self.last_anomaly}")
            self.auto_fix_pipeline()
        else:
            self.diff_count = 0
            self.last_anomaly = None
            self.status_msg = "HEALTHY"

        # Check submodules
        sub_output = self._run_cmd("git submodule status")
        if "-" in sub_output or "+" in sub_output:
            self.last_anomaly = "Submodule out of sync."
            logger.warning(f"[ShadowPilot] Anomaly: {self.last_anomaly}")
            self._run_cmd("git submodule update --init --recursive")
            self.status_msg = "HEALING"

    def auto_fix_pipeline(self):
        """Attempts to safely stash or log anomalies."""
        self.status_msg = "HEALING"
        logger.info("[ShadowPilot] Triggering CI Pipeline Auto-Fix...")
        # For safety in this demo, we just log instead of force wiping user changes.
        # But this is where the autonomous git reset/stash logic resides.
        # self._run_cmd("git stash -m 'ShadowPilot Auto-Fix'")

    async def run_loop(self):
        self.is_active = True
        logger.info("[ShadowPilot] Initialized and monitoring for anomalies.")
        while self.is_active:
            try:
                self.check_git_anomalies()
            except Exception as e:
                logger.error(f"[ShadowPilot] Loop Error: {e}")
            await asyncio.sleep(30) # Run every 30 seconds

shadow_pilot_instance = ShadowPilot()
