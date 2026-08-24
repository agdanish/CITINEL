"""OCSF schema constants, loaded from a pinned snapshot of the real schema.

Every class uid, category uid and activity enum in this module comes from a
snapshot of the OCSF project's own schema server (schema.ocsf.io/api), stored
alongside this file as `schema_snapshot.json` with its provenance recorded
inside it. Nothing here is transcribed from memory.

That matters more than it might look. Fetching rather than remembering caught
three errors before a line of mapping code existed:

  * Windows registry activity is class 201001/201002 in the `win` extension
    namespace, not 1008. 1008 is `event_log_actvity` -- and that missing "i"
    is OCSF's own spelling in the published schema, not a typo here.
  * `account_change` (3001) and `user_access` (3005) are both deprecated as of
    OCSF 1.9.0, superseded by `user_management` (3007).
  * `security_finding` (2001) is deprecated, superseded by `detection_finding`
    (2004) among others.

Version handling implements SDD Section 16 finding 7: OCSF requires every event
producer to declare `metadata.version`, so a consumer must branch on the
version the producer declared rather than assume one pinned version across all
source systems. `supports()` and `normalize_version()` below are that branch.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_SNAPSHOT = Path(__file__).parent / "schema_snapshot.json"

#: The OCSF version CITINEL emits. Written into every record's metadata.version.
OCSF_VERSION = "1.9.0"

#: Versions CITINEL knows how to consume. See `supports()`.
SUPPORTED_VERSIONS = ("1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9")

# --- severity, from the schema snapshot ------------------------------------
SEVERITY_UNKNOWN = 0
SEVERITY_INFORMATIONAL = 1
SEVERITY_LOW = 2
SEVERITY_MEDIUM = 3
SEVERITY_HIGH = 4
SEVERITY_CRITICAL = 5
SEVERITY_FATAL = 6
SEVERITY_OTHER = 99

# --- class uids -------------------------------------------------------------
FILE_ACTIVITY = 1001
MEMORY_ACTIVITY = 1004
MODULE_ACTIVITY = 1005
PROCESS_ACTIVITY = 1007
EVENT_LOG_ACTIVITY = 1008          # OCSF spells the class name "event_log_actvity"
VULNERABILITY_FINDING = 2002
DETECTION_FINDING = 2004
AUTHENTICATION = 3002
AUTHORIZE_SESSION = 3003
USER_MANAGEMENT = 3007             # supersedes deprecated 3001 / 3005
NETWORK_ACTIVITY = 4001
HTTP_ACTIVITY = 4002
DNS_ACTIVITY = 4003
SMB_ACTIVITY = 4006
REGISTRY_KEY_ACTIVITY = 201001     # win extension
REGISTRY_VALUE_ACTIVITY = 201002   # win extension
WINDOWS_RESOURCE_ACTIVITY = 201003  # win extension

#: Base-event attributes the schema marks required. `cloud` and `osint` are
#: also reported as required by the API because it flattens profile-attached
#: attributes; they apply only when those profiles are active, which they are
#: not for on-premise bank telemetry, so they are excluded here deliberately
#: rather than emitted empty.
BASE_REQUIRED = (
    "activity_id",
    "category_uid",
    "class_uid",
    "metadata",
    "severity_id",
    "time",
    "type_uid",
)

METADATA_REQUIRED = ("product", "version")


@lru_cache(maxsize=1)
def snapshot() -> dict:
    return json.loads(_SNAPSHOT.read_text())


@lru_cache(maxsize=1)
def classes() -> dict[str, dict]:
    return snapshot()["classes"]


@lru_cache(maxsize=1)
def _by_uid() -> dict[int, tuple[str, dict]]:
    return {v["uid"]: (name, v) for name, v in classes().items()}


def class_name(class_uid: int) -> str | None:
    entry = _by_uid().get(class_uid)
    return entry[0] if entry else None


def category_uid(class_uid: int) -> int | None:
    entry = _by_uid().get(class_uid)
    return entry[1]["category_uid"] if entry else None


def activities(class_uid: int) -> dict[int, str]:
    entry = _by_uid().get(class_uid)
    return {int(k): v for k, v in entry[1]["activities"].items()} if entry else {}


def type_uid(class_uid: int, activity_id: int) -> int:
    """The schema states producers MUST compute this as class_uid*100 + activity_id."""
    return class_uid * 100 + activity_id


def is_valid_activity(class_uid: int, activity_id: int) -> bool:
    return activity_id in activities(class_uid)


# --- producer-version handling (SDD Section 16 finding 7) -------------------

def normalize_version(declared: str) -> tuple[int, int] | None:
    """Parse a producer-declared metadata.version into (major, minor)."""
    if not declared:
        return None
    parts = declared.strip().lstrip("vV").split(".")
    try:
        return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        return None


def supports(declared: str) -> bool:
    """Whether CITINEL can consume records a producer declared at this version.

    Branching on the producer's declared version -- per event, not per
    deployment -- is the point of finding 7: different bank source systems
    adopt schema updates at different paces, so one pinned assumption across
    all of them is wrong by construction.
    """
    parsed = normalize_version(declared)
    if parsed is None:
        return False
    major, minor = parsed
    return f"{major}.{minor}" in SUPPORTED_VERSIONS
