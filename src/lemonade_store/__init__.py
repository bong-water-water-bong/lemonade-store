"""Lemonade Store — offline-first ma-and-pa retail suite (umbrella package).

This package defines the *contracts* every department repo
(lemonade-cashier, lemonade-inventory, lemonade-accounting,
lemonade-marketeer, lemonade-supplier, lemonade-reports, lemonade-site)
must agree on:

* the shared event envelope (`store.event.v1`),
* the department registry (who owns which events / approvals),
* the example store configuration (Tie Dye Farms).

No agents are implemented here. v0.1 is documentation + contracts only.
"""

from lemonade_store.config import (
    ConfigValidationError,
    StoreConfig,
    load_departments_file,
    load_store_config,
)
from lemonade_store.departments import (
    KNOWN_DEPARTMENTS,
    Department,
    DepartmentValidationError,
    registry,
)
from lemonade_store.events import (
    SCHEMA_VERSION,
    Actor,
    Event,
    EventValidationError,
    dump_event,
    load_event,
)

__all__ = [
    "SCHEMA_VERSION",
    "Actor",
    "ConfigValidationError",
    "Department",
    "DepartmentValidationError",
    "Event",
    "EventValidationError",
    "KNOWN_DEPARTMENTS",
    "StoreConfig",
    "dump_event",
    "load_departments_file",
    "load_event",
    "load_store_config",
    "registry",
]

__version__ = "0.1.0"
