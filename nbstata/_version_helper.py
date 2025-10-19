"""
Version helpers that avoid distutils and runtime pkg_resources.
"""
from __future__ import annotations
from packaging.version import Version, InvalidVersion

def version_at_least(v: str, minimum: str) -> bool:
    """
    Return True if version string v >= minimum using robust PEP 440 parsing.
    Replaces pkg_resources.parse_version / distutils.LooseVersion.
    """
    try:
        return Version(v) >= Version(minimum)
    except InvalidVersion:
        # Conservative fallback: treat unknown as not meeting the minimum
        return False
