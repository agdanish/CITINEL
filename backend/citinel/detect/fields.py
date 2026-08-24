"""Native field extraction for Sigma matching.

Sigma rules address events by their SOURCE's field names (Sysmon's `Image`,
Windows Security's `EventCode`, IIS's `cs-uri-stem`). This module produces that
native view. It is deliberately separate from OCSF normalization: OCSF is what
findings attach to; native fields are what community rules match against.
"""

from __future__ import annotations

import re

_SYSMON_DATA = re.compile(r"<Data Name='([^']+)'>([^<]*)</Data>")
_SYSMON_EVENTID = re.compile(r"<EventID>(\d+)</EventID>")
_SYSMON_COMPUTER = re.compile(r"<Computer>([^<]*)</Computer>")
_WIN_KV = re.compile(r"^([A-Za-z_]\w*)=(.*)$", re.MULTILINE)
_WIN_INDENT_KV = re.compile(r"^\s+([A-Za-z][\w \-/]*?):\s+(.+?)\s*$", re.MULTILINE)
_KV_QUOTED = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')

_IIS_COLS = (
    "date", "time", "s-ip", "cs-method", "cs-uri-stem", "cs-uri-query",
    "s-port", "cs-username", "c-ip", "cs(User-Agent)", "cs(Referer)",
    "sc-status", "sc-substatus", "sc-win32-status", "time-taken",
)


def native_fields(event_class: str, body: str) -> dict[str, str]:
    """Extract the source-native field dict Sigma rules address."""
    if event_class == "sysmon":
        fields = {k: v for k, v in _SYSMON_DATA.findall(body)}
        m = _SYSMON_EVENTID.search(body)
        if m:
            # Underscored: EventID is an attribute of the XML envelope, not a
            # <Data> field, but nearly every Sysmon rule dispatches on it.
            fields["_EventID"] = m.group(1)
        c = _SYSMON_COMPUTER.search(body)
        if c:
            fields["Computer"] = c.group(1)
        return fields

    if event_class.startswith("winevent:"):
        fields = {k: v.strip() for k, v in _WIN_KV.findall(body)}
        for k, v in _WIN_INDENT_KV.findall(body):
            key = k.strip().replace(" ", "")
            if key and key not in fields:
                fields[key] = v.strip()
        return fields

    if event_class in ("winregistry",) or event_class.startswith("fortinet:"):
        return {m[0]: (m[1] or m[2]) for m in _KV_QUOTED.findall(body)}

    if event_class == "iis":
        parts = body.strip().split(" ")
        fields = {}
        for i, col in enumerate(_IIS_COLS):
            if i < len(parts):
                fields[col] = parts[i]
        # Sigma webserver rules commonly address these generic names:
        fields.setdefault("cs-uri", fields.get("cs-uri-stem", ""))
        fields.setdefault("c-uri", fields.get("cs-uri-stem", ""))
        fields.setdefault("c-useragent", fields.get("cs(User-Agent)", ""))
        fields.setdefault("sc-status", fields.get("sc-status", ""))
        return fields

    # JSON sources (suricata, stream): flatten one level.
    if event_class.startswith(("suricata:", "stream:", "json:")):
        import json
        try:
            obj = json.loads(body)
        except ValueError:
            return {}
        flat: dict[str, str] = {}
        for k, v in obj.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if not isinstance(v2, (dict, list)):
                        flat[f"{k}.{k2}"] = str(v2)
            elif not isinstance(v, list):
                flat[k] = str(v)
        return flat

    return {}
