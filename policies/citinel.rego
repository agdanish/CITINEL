# CITINEL response policy -- Rego rendering.
#
# This file mirrors policies/citinel-policy.yaml clause for clause. The YAML
# is canonical and is what the in-process gate evaluates today (the fallback
# ladder's pre-committed second rung, CITINEL-STATE.md Section 1.7); this Rego
# exists so the real OPA engine can take over at deploy time evaluating the
# SAME rulebook. A conformance test must hold both engines to identical
# decisions over the golden cases before OPA becomes the active engine.
#
# input:  {"action_class": str, "assets_affected": int}
# output: data.citinel.response.decision -> {"verdict": ..., "clause": ...}

package citinel.response

clauses := {
    "enrich_ioc":      {"ref": "1.1", "tier": "autonomous", "approval_always": false, "max_assets_auto": 0, "reversible": true},
    "query_logs":      {"ref": "1.2", "tier": "autonomous", "approval_always": false, "max_assets_auto": 0, "reversible": true},
    "notify":          {"ref": "2.1", "tier": "autonomous", "approval_always": false, "max_assets_auto": 0, "reversible": false},
    "isolate_host":    {"ref": "3.1", "tier": "assist",     "approval_always": false, "max_assets_auto": 1, "reversible": true},
    "block_ip":        {"ref": "3.2", "tier": "assist",     "approval_always": false, "max_assets_auto": 3, "reversible": true},
    "quarantine_file": {"ref": "3.3", "tier": "assist",     "approval_always": false, "max_assets_auto": 5, "reversible": true},
    "revoke_sessions": {"ref": "4.1", "tier": "assist",     "approval_always": false, "max_assets_auto": 1, "reversible": false},
    "disable_account": {"ref": "4.2", "tier": "shadow",     "approval_always": true,  "max_assets_auto": 0, "reversible": true},
}

default decision := {"verdict": "deny", "clause": "-",
                     "reason": "undefined actions are denied, not defaulted"}

clause := clauses[input.action_class]

# Structural approval outranks every dial position.
decision := {"verdict": "require_approval", "clause": clause.ref,
             "reason": "approval is structural for this class"} if {
    clause.approval_always
}

# Blast radius beyond the automatic cap forces the approval path.
decision := {"verdict": "require_approval", "clause": clause.ref,
             "reason": "blast radius exceeds automatic cap"} if {
    not clause.approval_always
    input.assets_affected > clause.max_assets_auto
}

decision := {"verdict": "shadow", "clause": clause.ref,
             "reason": "shadow tier: propose only"} if {
    not clause.approval_always
    input.assets_affected <= clause.max_assets_auto
    clause.tier == "shadow"
}

decision := {"verdict": "allow_with_rollback", "clause": clause.ref,
             "reason": "assist tier, reversible"} if {
    not clause.approval_always
    input.assets_affected <= clause.max_assets_auto
    clause.tier == "assist"
    clause.reversible
}

decision := {"verdict": "allow", "clause": clause.ref,
             "reason": "assist tier, irreversible within hard cap"} if {
    not clause.approval_always
    input.assets_affected <= clause.max_assets_auto
    clause.tier == "assist"
    not clause.reversible
}

decision := {"verdict": "allow", "clause": clause.ref,
             "reason": "autonomous tier"} if {
    not clause.approval_always
    input.assets_affected <= clause.max_assets_auto
    clause.tier == "autonomous"
}
