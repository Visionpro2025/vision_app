from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass
from config.settings import SEC

@dataclass
class AuditEvent:
    actor: str
    action: str
    resource: str
    outcome: str


audit_log = []

# Stubs simples para crecer luego

def mask_pii(text: str) -> str:
    if not SEC.pii_masking: return text
    return text.replace("@", "[at]")  # ejemplo simplista


def audit(event: AuditEvent):
    audit_log.append(event)

