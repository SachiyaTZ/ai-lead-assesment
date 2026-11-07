import re
from dataclasses import dataclass

SUSPICIOUS=[
    r"ignore\s+(all|any|the)?\s*(previous|prior|system)\s+instructions",
    r"reveal\s+(the\s+)?(system prompt|secret|password|api key)",
    r"bypass\s+(security|authorization|rbac)",
    r"act\s+as\s+(an?\s+)?administrator",
    r"exfiltrat(e|ion)",
]
@dataclass
class SecurityResult:
    allowed: bool; reasons: list[str]

def scan_user_input(text: str) -> SecurityResult:
    reasons=[p for p in SUSPICIOUS if re.search(p,text,re.I)]
    return SecurityResult(not reasons,reasons)

def sanitize_retrieved_content(text: str) -> tuple[str,list[str]]:
    flags=[p for p in SUSPICIOUS if re.search(p,text,re.I)]
    # Preserve evidence but clearly mark malicious instructions as untrusted content.
    cleaned=text.replace("IMPORTANT SYSTEM MESSAGE:","[UNTRUSTED DOCUMENT TEXT]:")
    return cleaned, flags
