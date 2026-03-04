"""
Shared dataclasses used across the broker_app package.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PersonalInfo:
    """Personal information used to fill opt-out forms."""
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip_code: str
    date_of_birth: str = ""
    middle_name: str = ""


@dataclass
class BrokerSite:
    """Describes a single data-broker opt-out target."""
    name: str
    url: str
    opt_out_url: str
    form_fields: Dict[str, str]
    instructions: str = ""
    difficulty: str = "medium"   # easy | medium | hard
    requires_verification: bool = False
