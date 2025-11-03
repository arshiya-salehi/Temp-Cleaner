"""
Preconfigured Windows CMD tasks and runner utilities.

Each task maps a friendly name to a command string. The GUI can
import `TASKS` or call `list_tasks()` to build buttons dynamically.

The `run_task(cmd)` function runs the command and returns a dict with
`returncode`, `stdout`, and `stderr`.
"""
from typing import Dict
import subprocess

# Predefined tasks. Add more tasks here as needed.
TASKS = {
    "GP Update (force)": "gpupdate /force",
    "Flush DNS": "ipconfig /flushdns",
    "Release IP": "ipconfig /release",
    "Renew IP": "ipconfig /renew",
}

# Short descriptions for each task (used for tooltips)
TASK_DESCRIPTIONS = {
    "GP Update (force)": "Force a Group Policy update on the local machine (gpupdate /force). Useful after changing GPOs.",
    "Flush DNS": "Clear the local DNS resolver cache (ipconfig /flushdns). Helps when DNS changes aren't reflected locally.",
    "Release IP": "Release the current DHCP lease (ipconfig /release). This will temporarily drop IPv4 connectivity.",
    "Renew IP": "Request a new DHCP lease from the server (ipconfig /renew) after releasing.",
}


def get_task_description(name: str) -> str:
    """Return a short description for task `name` or empty string if unknown."""
    return TASK_DESCRIPTIONS.get(name, "")


def list_tasks() -> Dict[str, str]:
    """Return a copy of available tasks mapping name -> command string."""
    return dict(TASKS)


def run_task(cmd: str, timeout: int = 300) -> Dict[str, str]:
    """Run a command via the Windows shell and capture output.

    Args:
        cmd: Command string to execute (executed via the shell).
        timeout: Optional timeout in seconds.

    Returns:
        A dict: {"returncode": int, "stdout": str, "stderr": str}
    """
    try:
        completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {"returncode": -1, "stdout": "", "stderr": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}
