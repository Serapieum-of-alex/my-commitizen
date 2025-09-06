from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

# Keep a set of seen entries to avoid duplicates within a single changelog run
_seen: set[Tuple[Optional[str], Optional[str], str]] = set()

# Regex to strip a trailing PR reference like " (#123)"
_PR_TRAIL_RE = re.compile(r"\s*\(#\d+\)\s*$", flags=re.IGNORECASE)

# Regex to roughly capture the conventional header before the colon
# e.g., "feat(plot)!: something" -> we only want the part after the first ':'
_HEADER_SPLIT_RE = re.compile(r":\s*")


def _strip_pr_ref(text: str) -> str:
    return _PR_TRAIL_RE.sub("", text or "").strip()


def _fallback_subject_from_message(message: str) -> str:
    if not message:
        return ""
    first_line = (message.splitlines() or [""])[0].strip()
    # Remove leading type(scope)!: if present by splitting on the first ':'
    parts = _HEADER_SPLIT_RE.split(first_line, maxsplit=1)
    if len(parts) == 2:
        candidate = parts[1].strip()
    else:
        candidate = first_line
    return _strip_pr_ref(candidate)


def normalize_and_dedup(entry: Dict[str, Any], commit: Any) -> Dict[str, Any] | None:
    """
    Commitizen changelog hook:
    - Normalize the subject: strip trailing PR numbers like " (#123)".
    - If the parsed subject is empty, try to derive it from commit body/message.
    - De-duplicate entries by (type, scope, normalized_subject_lower).
    Return None to drop a duplicate entry.
    """
    subject = (entry.get("subject") or "").strip()
    subject = _strip_pr_ref(subject)

    if not subject:
        # Prefer extracting from commit body: first non-empty line
        body = getattr(commit, "body", "") or ""
        picked = ""
        for line in (body.splitlines() or []):
            ln = line.strip()
            if not ln:
                continue
            # remove list markers like '- ' or '* '
            ln = re.sub(r"^[-*]\s+", "", ln)
            picked = ln
            break
        if not picked:
            # Fallback to parsing the header line
            raw_message = getattr(commit, "message", "") or ""
            picked = _fallback_subject_from_message(raw_message)
        subject = _strip_pr_ref(picked)

    # Persist the normalized subject back to the entry so the template renders it
    entry["subject"] = subject
    # Some templates may render `message` instead of `subject`; keep them in sync
    if subject:
        entry["message"] = subject

    norm_key = (subject or "").lower().strip()
    change_type = entry.get("change_type") or entry.get("type")
    key = (change_type, entry.get("scope"), norm_key)

    if not subject:
        # Drop entries with empty subject to avoid empty bullets
        return None

    if key in _seen:
        return None

    _seen.add(key)
    return entry
