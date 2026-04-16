from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal


Severity = Literal["role-marker", "jailbreak", "forged-firewall", "role-tag"]


@dataclass(frozen=True)
class PatternSpec:
    pattern_id: str
    severity: Severity
    regex: re.Pattern[str]


_FLAGS = re.IGNORECASE | re.MULTILINE

PATTERNS: tuple[PatternSpec, ...] = (
    PatternSpec(
        pattern_id="role-marker-en",
        severity="role-marker",
        regex=re.compile(r"\[\s*(SYSTEM|USER|ASSISTANT|INST)\s*\]", _FLAGS),
    ),
    PatternSpec(
        pattern_id="role-marker-ko",
        severity="role-marker",
        regex=re.compile(r"\[\s*(시스템|사용자|지시)\s*\]", _FLAGS),
    ),
    PatternSpec(
        pattern_id="chatml-token",
        severity="role-marker",
        regex=re.compile(r"<\|im_(start|end)\|>|<\|endoftext\|>", _FLAGS),
    ),
    PatternSpec(
        pattern_id="role-tag-xml",
        severity="role-tag",
        regex=re.compile(r"</?\s*(system|user|assistant|instructions?)\s*>", _FLAGS),
    ),
    PatternSpec(
        pattern_id="jailbreak-en",
        severity="jailbreak",
        regex=re.compile(
            r"ignore (all |previous |the above )?instructions|"
            r"disregard (prior|previous) (instructions|rules)|"
            r"you are now",
            _FLAGS,
        ),
    ),
    PatternSpec(
        pattern_id="jailbreak-ko",
        severity="jailbreak",
        regex=re.compile(
            r"(이전|앞선) 지시를?\s*(무시|넘어|해제)|"
            r"지금부터 너는|"
            r"새로운 역할은",
            _FLAGS,
        ),
    ),
    PatternSpec(
        pattern_id="forged-firewall",
        severity="forged-firewall",
        regex=re.compile(
            r"\[\s*(AUDIENCE FIREWALL|SAFETY OVERRIDE|END OF UNTRUSTED)\s*\]",
            _FLAGS,
        ),
    ),
)
