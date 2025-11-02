# config.py
"""
Configuration and path resolvers for Temp-Cleaner.

Provides functions that return pathlib.Path objects for common
Windows cleanup targets (system temp, user %TEMP%, Prefetch, Recent,
etc.). Also exposes a TARGETS mapping used by the GUI.
"""
from pathlib import Path
import os
import tempfile


def get_system_temp() -> Path:
	"""Return the OS temp folder (typically C:\\Windows\\Temp or from tempfile.gettempdir())."""
	return Path(tempfile.gettempdir())


def get_user_env_temp() -> Path:
	"""Return the currently-active user's %TEMP% (or TMP) environment variable."""
	tmp = os.environ.get("TEMP") or os.environ.get("TMP")
	if tmp:
		return Path(tmp)
	return get_system_temp()


def get_windows_prefetch() -> Path:
	"""Return the Windows Prefetch folder (C:\\Windows\\Prefetch).

	Note: Accessing Prefetch may require elevated permissions and
	deleting it is not usually recommended on managed systems.
	"""
	system_root = os.environ.get("SystemRoot", r"C:\\Windows")
	return Path(system_root) / "Prefetch"



def get_recent_folder() -> Path:
	"""Return the user's Recent folder (e.g., C:\\Users\\<user>\\Recent)."""
	userprof = os.environ.get("USERPROFILE")
	if userprof:
		return Path(userprof) / "Recent"
	# Fallback: try HOME
	home = os.environ.get("HOME")
	if home:
		return Path(home) / "Recent"
	return Path(tempfile.gettempdir())


def get_windows_folder_tmp() -> Path:
	"""Return Windows directory's Temp folder (usually C:\\Windows\\Temp)."""
	system_root = os.environ.get("SystemRoot", r"C:\\Windows")
	return Path(system_root) / "Temp"


# Mapping of display name -> callable that returns a Path for that target.
TARGETS = {
	"User %TEMP%": get_user_env_temp,
	"Windows Temp": get_windows_folder_tmp,
	"Prefetch": get_windows_prefetch,
	"Recent": get_recent_folder,
}


def list_targets() -> dict:
	"""Return a dict copy of current targets name -> Path (callables invoked).

	This is used by the GUI to build buttons dynamically.
	"""
	return {name: fn() for name, fn in TARGETS.items()}

