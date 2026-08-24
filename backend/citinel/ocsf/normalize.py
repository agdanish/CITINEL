"""Normalize heterogeneous bank telemetry into OCSF 1.9.0 records.

This is the layer that makes "a new source is a mapping, not a rebuild" (deck
slide 11) literally true: every downstream stage -- Sigma matching, the agent
swarm, the policy gate, the compliance drafter -- reads one schema and never
learns what a Sysmon XML document or a Fortinet syslog line looks like.

Mapping targets come from `schema.py`, which loads a pinned snapshot of OCSF's
own published schema. Activity ids are validated against that snapshot rather
than trusted, so a mapping that names an activity the class does not define is
caught here instead of producing a plausible-looking but invalid record.

Performance note: these run over roughly 950,000 events, so field extraction is
done with compiled regexes rather than a full XML/JSON object parse wherever
the needed fields are shallow.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Callable

from citinel.ocsf import schema as S

# --- shallow field extraction ----------------------------------------------
_SYSMON_EVENTID = re.compile(r"<EventID>(\d+)</EventID>")
_SYSMON_DATA = re.compile(r"<Data Name='([^']+)'>([^<]*)</Data>")
_SYSMON_COMPUTER = re.compile(r"<Computer>([^<]*)</Computer>")

_WIN_KV = re.compile(r"^([A-Za-z_]\w*)=(.*)$", re.MULTILINE)
_WIN_INDENT_KV = re.compile(r"^\s+([A-Za-z][\w \-/]*?):\s+(.+?)\s*$", re.MULTILINE)

_FGT_KV = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')
# Some IIS records in this corpus are truncated mid-line, carrying only the
# leading fields. Require the five that identify the request; the rest are
# optional so a short line is still mapped rather than dropped.
_IIS_FIELDS = re.compile(
    r"^(?P<date>\S+) (?P<time>\S+) (?P<s_ip>\S+) (?P<method>[A-Z]+) (?P<uri>\S+)"
    r"(?: (?P<query>\S+))?(?: (?P<port>\S+))?(?: (?P<user>\S+))?(?: (?P<c_ip>\S+))?"
)

_HTTP_ACTIVITY = {
    "CONNECT": 1, "DELETE": 2, "GET": 3, "HEAD": 4, "OPTIONS": 5,
    "POST": 6, "PUT": 7, "TRACE": 8, "PATCH": 9,
}


def _sysmon_fields(body: str) -> dict[str, str]:
    return {k: v for k, v in _SYSMON_DATA.findall(body)}


def _win_fields(body: str) -> dict[str, str]:
    fields = {k: v.strip() for k, v in _WIN_KV.findall(body)}
    # The Message block carries indented "Key:  Value" pairs holding the
    # security-relevant detail (account names, logon type, process paths).
    for k, v in _WIN_INDENT_KV.findall(body):
        key = k.strip().replace(" ", "")
        if key and key not in fields:
            fields[key] = v.strip()
    return fields


def _fgt_fields(body: str) -> dict[str, str]:
    return {m[0]: (m[1] or m[2]) for m in _FGT_KV.findall(body)}


# --- record construction ----------------------------------------------------

def _base(
    *,
    class_uid: int,
    activity_id: int,
    severity_id: int,
    time_ms: int,
    original_time: str,
    product_name: str,
    log_name: str,
    raw: str,
) -> dict[str, Any]:
    """Assemble the OCSF base-event fields every record must carry."""
    if not S.is_valid_activity(class_uid, activity_id):
        # Fall back to the class's own "Unknown" rather than emit an activity
        # the schema does not define for this class.
        activity_id = 0
    return {
        "class_uid": class_uid,
        "category_uid": S.category_uid(class_uid),
        "activity_id": activity_id,
        "type_uid": S.type_uid(class_uid, activity_id),
        "severity_id": severity_id,
        "time": time_ms,
        "metadata": {
            # metadata.product and metadata.version are the two attributes OCSF
            # marks required on the metadata object itself.
            "product": {
                "name": product_name,
                "vendor_name": "Splunk BOTS v1 (CC0) replay",
                "version": "1",
            },
            "version": S.OCSF_VERSION,
            "log_name": log_name,
            "original_time": original_time,
        },
        "raw_data": raw,
    }


# --- per-source mappers -----------------------------------------------------

_SYSMON_MAP: dict[int, tuple[int, int]] = {
    1:  (S.PROCESS_ACTIVITY, 1),            # Process Create -> Launch
    2:  (S.FILE_ACTIVITY, 6),               # File creation time changed
    3:  (S.NETWORK_ACTIVITY, 1),            # Network connection -> Open
    4:  (S.EVENT_LOG_ACTIVITY, 0),          # Sysmon service state changed
    5:  (S.PROCESS_ACTIVITY, 2),            # Process terminated
    6:  (S.MODULE_ACTIVITY, 1),             # Driver loaded
    7:  (S.MODULE_ACTIVITY, 1),             # Image loaded
    8:  (S.PROCESS_ACTIVITY, 4),            # CreateRemoteThread -> Inject
    9:  (S.FILE_ACTIVITY, 2),               # RawAccessRead
    10: (S.PROCESS_ACTIVITY, 3),            # ProcessAccess -> Open
    11: (S.FILE_ACTIVITY, 1),               # FileCreate
    12: (S.REGISTRY_KEY_ACTIVITY, 1),       # Registry object create/delete
    13: (S.REGISTRY_VALUE_ACTIVITY, 2),     # Registry value set
    14: (S.REGISTRY_KEY_ACTIVITY, 5),       # Registry key/value rename
    15: (S.FILE_ACTIVITY, 1),               # FileCreateStreamHash
    16: (S.EVENT_LOG_ACTIVITY, 0),          # Sysmon config change
    17: (S.WINDOWS_RESOURCE_ACTIVITY, 1),   # Pipe created
    18: (S.WINDOWS_RESOURCE_ACTIVITY, 1),   # Pipe connected
    22: (S.DNS_ACTIVITY, 1),                # DNS query
    23: (S.FILE_ACTIVITY, 4),               # FileDelete
}


def _map_sysmon(body: str, ts: int, original: str) -> dict[str, Any] | None:
    m = _SYSMON_EVENTID.search(body)
    if not m:
        return None
    event_id = int(m.group(1))
    class_uid, activity_id = _SYSMON_MAP.get(event_id, (S.EVENT_LOG_ACTIVITY, 0))
    f = _sysmon_fields(body)
    comp = _SYSMON_COMPUTER.search(body)

    rec = _base(
        class_uid=class_uid, activity_id=activity_id,
        severity_id=S.SEVERITY_INFORMATIONAL, time_ms=ts, original_time=original,
        product_name="Microsoft Sysmon", log_name="Microsoft-Windows-Sysmon/Operational",
        raw=body,
    )
    rec["device"] = {"hostname": comp.group(1) if comp else f.get("Computer", "")}
    rec["_source_event_id"] = event_id

    if f.get("Image"):
        rec["process"] = {
            "file": {"path": f.get("Image"), "name": f.get("Image", "").rsplit("\\", 1)[-1]},
            "cmd_line": f.get("CommandLine"),
            "pid": _int(f.get("ProcessId")),
            "uid": f.get("ProcessGuid"),
            "user": {"name": f.get("User")},
        }
    if f.get("ParentImage"):
        rec.setdefault("actor", {})["process"] = {
            "file": {"path": f.get("ParentImage")},
            "cmd_line": f.get("ParentCommandLine"),
            "pid": _int(f.get("ParentProcessId")),
        }
    if f.get("TargetFilename"):
        rec["file"] = {"path": f.get("TargetFilename"),
                       "name": f.get("TargetFilename", "").rsplit("\\", 1)[-1]}
    if f.get("TargetObject"):
        rec["reg_key"] = {"path": f.get("TargetObject")}
        if f.get("Details"):
            rec["reg_value"] = {"name": f.get("TargetObject", "").rsplit("\\", 1)[-1],
                                "data": {"string_t": f.get("Details")}}
    if f.get("DestinationIp") or f.get("SourceIp"):
        rec["src_endpoint"] = {"ip": f.get("SourceIp"), "port": _int(f.get("SourcePort"))}
        rec["dst_endpoint"] = {"ip": f.get("DestinationIp"),
                               "port": _int(f.get("DestinationPort")),
                               "hostname": f.get("DestinationHostname")}
    if f.get("QueryName"):
        rec["query"] = {"hostname": f.get("QueryName")}
    if f.get("Hashes"):
        rec.setdefault("file", {})["hashes"] = _parse_hashes(f["Hashes"])
    return rec


_WINSEC_MAP: dict[int, tuple[int, int]] = {
    1102: (S.EVENT_LOG_ACTIVITY, 1),        # audit log cleared
    4624: (S.AUTHENTICATION, 1),            # successful logon
    4625: (S.AUTHENTICATION, 1),            # failed logon
    4634: (S.AUTHENTICATION, 2),            # logoff
    4647: (S.AUTHENTICATION, 2),            # user-initiated logoff
    4648: (S.AUTHENTICATION, 1),            # logon with explicit credentials
    4656: (S.WINDOWS_RESOURCE_ACTIVITY, 1),
    4658: (S.WINDOWS_RESOURCE_ACTIVITY, 1),
    4663: (S.WINDOWS_RESOURCE_ACTIVITY, 1),
    4664: (S.FILE_ACTIVITY, 1),             # attempt to create a hard link
    4672: (S.AUTHORIZE_SESSION, 1),         # special privileges assigned
    4674: (S.AUTHORIZE_SESSION, 1),         # privileged service operation
    4703: (S.AUTHORIZE_SESSION, 1),         # token right adjusted
    4688: (S.PROCESS_ACTIVITY, 1),          # process created
    4689: (S.PROCESS_ACTIVITY, 2),          # process exited
    4720: (S.USER_MANAGEMENT, 1),           # account created
    4722: (S.USER_MANAGEMENT, 4),           # account enabled
    4725: (S.USER_MANAGEMENT, 5),           # account disabled
    4726: (S.USER_MANAGEMENT, 3),           # account deleted
    4738: (S.USER_MANAGEMENT, 2),           # account changed
    4740: (S.USER_MANAGEMENT, 6),           # account locked out
    4768: (S.AUTHENTICATION, 3),            # Kerberos TGT requested
    4769: (S.AUTHENTICATION, 4),            # Kerberos service ticket
    4771: (S.AUTHENTICATION, 6),            # Kerberos preauth failed
    4776: (S.AUTHENTICATION, 1),            # credential validation
    5140: (S.SMB_ACTIVITY, 2),              # network share accessed
    5145: (S.SMB_ACTIVITY, 2),
}

#: Event codes that describe a failure and therefore warrant more than
#: informational severity on their own.
_WINSEC_FAILURE = {4625, 4771, 4740, 1102}


def _map_winclassic(body: str, ts: int, original: str, log_hint: str) -> dict[str, Any] | None:
    f = _win_fields(body)
    code = _int(f.get("EventCode"))
    if code is None:
        return None
    log_name = f.get("LogName", log_hint)
    if log_name.lower() == "security":
        class_uid, activity_id = _WINSEC_MAP.get(code, (S.EVENT_LOG_ACTIVITY, 0))
    else:
        class_uid, activity_id = (S.EVENT_LOG_ACTIVITY, 0)

    severity = S.SEVERITY_MEDIUM if code in _WINSEC_FAILURE else S.SEVERITY_INFORMATIONAL
    rec = _base(
        class_uid=class_uid, activity_id=activity_id, severity_id=severity,
        time_ms=ts, original_time=original,
        product_name="Microsoft Windows Event Log",
        log_name=f"WinEventLog:{log_name}", raw=body,
    )
    rec["device"] = {"hostname": f.get("ComputerName", "")}
    rec["_source_event_id"] = code
    rec["message"] = f.get("Message", "")[:500]

    account = f.get("AccountName") or f.get("SubjectUserName")
    if account:
        rec["user"] = {"name": account, "domain": f.get("AccountDomain")}
    if f.get("LogonType"):
        rec["logon_type_id"] = _int(f.get("LogonType"))
    if f.get("SourceNetworkAddress"):
        rec["src_endpoint"] = {"ip": f.get("SourceNetworkAddress"),
                               "port": _int(f.get("SourcePort"))}
    if f.get("NewProcessName") or f.get("ProcessName"):
        rec["process"] = {"file": {"path": f.get("NewProcessName") or f.get("ProcessName")},
                          "cmd_line": f.get("ProcessCommandLine")}
    if f.get("ObjectName"):
        rec["file"] = {"path": f.get("ObjectName")}
    if code in _WINSEC_FAILURE:
        rec["status_id"] = 2  # Failure
    return rec


_SURICATA_SEVERITY = {1: S.SEVERITY_HIGH, 2: S.SEVERITY_MEDIUM, 3: S.SEVERITY_LOW}


def _map_suricata(body: str, ts: int, original: str) -> dict[str, Any] | None:
    try:
        o = json.loads(body)
    except ValueError:
        return None
    etype = o.get("event_type", "")

    if etype == "alert":
        alert = o.get("alert", {})
        class_uid, activity_id = S.DETECTION_FINDING, 1
        severity = _SURICATA_SEVERITY.get(alert.get("severity"), S.SEVERITY_MEDIUM)
    elif etype == "dns":
        class_uid, activity_id = S.DNS_ACTIVITY, 1 if o.get("dns", {}).get("type") == "query" else 2
        severity = S.SEVERITY_INFORMATIONAL
    elif etype == "http":
        method = str(o.get("http", {}).get("http_method", "")).upper()
        class_uid, activity_id = S.HTTP_ACTIVITY, _HTTP_ACTIVITY.get(method, 0)
        severity = S.SEVERITY_INFORMATIONAL
    elif etype in ("flow", "netflow", "tls", "fileinfo", "smtp", "ssh"):
        class_uid, activity_id = S.NETWORK_ACTIVITY, 6
        severity = S.SEVERITY_INFORMATIONAL
    else:
        class_uid, activity_id = S.EVENT_LOG_ACTIVITY, 0
        severity = S.SEVERITY_INFORMATIONAL

    rec = _base(
        class_uid=class_uid, activity_id=activity_id, severity_id=severity,
        time_ms=ts, original_time=original, product_name="Suricata IDS",
        log_name=f"suricata:{etype}", raw=body,
    )
    if o.get("src_ip"):
        rec["src_endpoint"] = {"ip": o.get("src_ip"), "port": o.get("src_port")}
    if o.get("dest_ip"):
        rec["dst_endpoint"] = {"ip": o.get("dest_ip"), "port": o.get("dest_port")}
    if etype == "alert":
        a = o.get("alert", {})
        rec["finding_info"] = {
            "title": a.get("signature"),
            "uid": str(a.get("signature_id")),
            "types": [a.get("category")] if a.get("category") else [],
        }
        rec["risk_level_id"] = severity
    if etype == "dns":
        rec["query"] = {"hostname": o.get("dns", {}).get("rrname"),
                        "type": o.get("dns", {}).get("rrtype")}
    if etype == "http":
        h = o.get("http", {})
        rec["http_request"] = {"url": {"hostname": h.get("hostname"), "path": h.get("url")},
                               "http_method": h.get("http_method"),
                               "user_agent": h.get("http_user_agent")}
    return rec


def _map_stream(body: str, ts: int, original: str, subtype: str) -> dict[str, Any] | None:
    try:
        o = json.loads(body)
    except ValueError:
        return None
    if subtype == "http":
        class_uid = S.HTTP_ACTIVITY
        activity_id = _HTTP_ACTIVITY.get(str(o.get("http_method", "")).upper(), 0)
    elif subtype == "dns":
        class_uid, activity_id = S.DNS_ACTIVITY, 1
    elif subtype == "smb":
        class_uid, activity_id = S.SMB_ACTIVITY, 2
    else:
        class_uid, activity_id = S.NETWORK_ACTIVITY, 6

    rec = _base(
        class_uid=class_uid, activity_id=activity_id,
        severity_id=S.SEVERITY_INFORMATIONAL, time_ms=ts, original_time=original,
        product_name="Splunk Stream", log_name=f"stream:{subtype}", raw=body,
    )
    rec["src_endpoint"] = {"ip": o.get("src_ip"), "port": o.get("src_port"),
                           "mac": o.get("src_mac")}
    rec["dst_endpoint"] = {"ip": o.get("dest_ip"), "port": o.get("dest_port"),
                           "mac": o.get("dest_mac")}
    rec["traffic"] = {"bytes_in": o.get("bytes_in"), "bytes_out": o.get("bytes_out"),
                      "packets_in": o.get("packets_in"), "packets_out": o.get("packets_out")}
    return rec


def _map_fortinet(body: str, ts: int, original: str, subtype: str) -> dict[str, Any] | None:
    f = _fgt_fields(body)
    if subtype == "utm":
        class_uid, activity_id = S.DETECTION_FINDING, 1
        severity = {"critical": S.SEVERITY_CRITICAL, "high": S.SEVERITY_HIGH,
                    "medium": S.SEVERITY_MEDIUM, "warning": S.SEVERITY_MEDIUM,
                    "low": S.SEVERITY_LOW}.get(f.get("level", ""), S.SEVERITY_MEDIUM)
    elif subtype == "traffic":
        class_uid, activity_id, severity = S.NETWORK_ACTIVITY, 6, S.SEVERITY_INFORMATIONAL
    else:
        class_uid, activity_id, severity = S.EVENT_LOG_ACTIVITY, 0, S.SEVERITY_INFORMATIONAL

    rec = _base(
        class_uid=class_uid, activity_id=activity_id, severity_id=severity,
        time_ms=ts, original_time=original, product_name="Fortinet FortiGate",
        log_name=f"fgt_{subtype}", raw=body,
    )
    rec["device"] = {"hostname": f.get("devname"), "uid": f.get("devid")}
    rec["src_endpoint"] = {"ip": f.get("srcip"), "port": _int(f.get("srcport"))}
    rec["dst_endpoint"] = {"ip": f.get("dstip"), "port": _int(f.get("dstport"))}
    if subtype == "utm":
        rec["finding_info"] = {"title": f.get("attack") or f.get("virus") or f.get("subtype"),
                               "uid": f.get("logid")}
    return rec


def _map_iis(body: str, ts: int, original: str) -> dict[str, Any] | None:
    m = _IIS_FIELDS.match(body.strip())
    if not m:
        return None
    g = m.groupdict()
    rec = _base(
        class_uid=S.HTTP_ACTIVITY,
        activity_id=_HTTP_ACTIVITY.get(g["method"].upper(), 0),
        severity_id=S.SEVERITY_INFORMATIONAL, time_ms=ts, original_time=original,
        product_name="Microsoft IIS", log_name="iis", raw=body,
    )
    rec["src_endpoint"] = {"ip": g.get("c_ip")}
    rec["dst_endpoint"] = {"ip": g["s_ip"], "port": _int(g.get("port"))}
    query = g.get("query")
    rec["http_request"] = {
        "http_method": g["method"],
        "url": {"path": g["uri"], "query_string": None if query in ("-", None) else query},
    }
    if g.get("user") and g["user"] != "-":
        rec["user"] = {"name": g["user"]}
    return rec


_REGISTRY_MAP = {
    "createkey": (S.REGISTRY_KEY_ACTIVITY, 1),
    "openkey": (S.REGISTRY_KEY_ACTIVITY, 2),
    "deletekey": (S.REGISTRY_KEY_ACTIVITY, 4),
    "setvalue": (S.REGISTRY_VALUE_ACTIVITY, 2),
    "deletevalue": (S.REGISTRY_VALUE_ACTIVITY, 4),
    "queryvalue": (S.REGISTRY_VALUE_ACTIVITY, 1),
}


def _map_winregistry(body: str, ts: int, original: str) -> dict[str, Any] | None:
    f = _fgt_fields(body)  # same key="value" shape
    rtype = str(f.get("registry_type", "")).lower()
    class_uid, activity_id = _REGISTRY_MAP.get(rtype, (S.REGISTRY_KEY_ACTIVITY, 0))
    rec = _base(
        class_uid=class_uid, activity_id=activity_id,
        severity_id=S.SEVERITY_INFORMATIONAL, time_ms=ts, original_time=original,
        product_name="Microsoft Windows Registry", log_name="WinRegistry", raw=body,
    )
    rec["reg_key"] = {"path": f.get("key_path")}
    if f.get("process_image"):
        rec["process"] = {"file": {"path": f.get("process_image")}, "pid": _int(f.get("pid"))}
    return rec


def _map_nessus(body: str, ts: int, original: str) -> dict[str, Any] | None:
    try:
        o = json.loads(body)
    except ValueError:
        return None
    rec = _base(
        class_uid=S.VULNERABILITY_FINDING, activity_id=1,
        severity_id=S.SEVERITY_MEDIUM, time_ms=ts, original_time=original,
        product_name="Tenable Nessus", log_name="nessus:scan", raw=body,
    )
    rec["finding_info"] = {"title": o.get("policy") or o.get("scan_type"),
                           "uid": str(o.get("plugin_id") or o.get("sid") or "")}
    rec["device"] = {"hostname": o.get("hostname")}
    return rec


# --- helpers ----------------------------------------------------------------

def _int(v: Any) -> int | None:
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def _parse_hashes(value: str) -> list[dict[str, str]]:
    """Sysmon writes 'SHA1=...,MD5=...,SHA256=...' in one field."""
    out = []
    for part in value.split(","):
        if "=" in part:
            algo, _, digest = part.partition("=")
            out.append({"algorithm": algo.strip(), "value": digest.strip()})
    return out


# --- entry point ------------------------------------------------------------

def normalize(event: dict) -> dict[str, Any] | None:
    """Map one extracted raw event onto an OCSF record, or None if unmappable."""
    cls = event.get("event_class", "")
    body = event.get("body", "")
    original = event.get("timestamp", "")
    try:
        ts = int(datetime.fromisoformat(original).timestamp() * 1000)
    except (ValueError, TypeError):
        return None

    if cls == "sysmon":
        return _map_sysmon(body, ts, original)
    if cls.startswith("winevent:"):
        return _map_winclassic(body, ts, original, cls.split(":", 1)[1])
    if cls.startswith("suricata:"):
        return _map_suricata(body, ts, original)
    if cls.startswith("stream:"):
        return _map_stream(body, ts, original, cls.split(":", 1)[1])
    if cls.startswith("fortinet:"):
        return _map_fortinet(body, ts, original, cls.split(":", 1)[1])
    if cls == "iis":
        return _map_iis(body, ts, original)
    if cls == "winregistry":
        return _map_winregistry(body, ts, original)
    if cls == "json:other":
        return _map_nessus(body, ts, original)
    return None
