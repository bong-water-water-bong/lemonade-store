"""The department registry.

Each Lemonade Store department repo registers what it does, what it
reads/writes, and what its agents need owner approval for. The registry
is intentionally a *static* Python literal — adding a department is a
code change and a review, not a runtime config tweak. This keeps the
v0.1 contract auditable and lets every consumer pin its expectations.

Two field pairs do related-but-distinct work:

* `consumes` / `emits` are the v0.1 *named* event types a department
  reads or produces today. They are advisory and will grow.
* `reads` / `writes` are the *allowed namespaces* a department may
  ever read from / write to. They are the security perimeter: if a
  department tries to write outside its `writes` prefixes, that's a
  contract violation. Today every department writes only its own
  namespace; we still spell it out so future "audit.*" or "store.*"
  shared namespaces can be added explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

KNOWN_DEPARTMENTS: frozenset[str] = frozenset(
    {
        "cashier",
        "inventory",
        "accounting",
        "marketeer",
        "supplier",
        "reports",
        "site",
    }
)


class DepartmentValidationError(ValueError):
    """Raised when a `Department` definition violates the v0.1 contract."""


@dataclass(frozen=True)
class Department:
    name: str
    repo: str
    namespace: str = ""  # event prefix; defaults to `name`
    owns: tuple[str, ...] = ()
    consumes: tuple[str, ...] = ()
    emits: tuple[str, ...] = ()
    agents: tuple[str, ...] = ()
    requires_owner_approval_for: tuple[str, ...] = ()
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    proposals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Fill in the default namespace lazily so callers can omit it.
        if not self.namespace:
            object.__setattr__(self, "namespace", self.name)
        _validate_department(self)


def _validate_department(dept: Department) -> None:
    ns_prefix = f"{dept.namespace}."
    for emit in dept.emits:
        if not emit.startswith(ns_prefix):
            raise DepartmentValidationError(
                f"department {dept.name!r} emits {emit!r}, "
                f"which is not in its namespace {dept.namespace!r}"
            )
    for write in dept.writes:
        if not write.startswith(ns_prefix):
            raise DepartmentValidationError(
                f"department {dept.name!r} declares writes={write!r}, "
                f"which is outside its namespace {dept.namespace!r}"
            )


# Marketeer is the only department whose event namespace differs from
# its name: the *repo* is `lemonade-marketeer` (matching the suite
# naming convention) but the *events* are `marketing.*` because that
# reads naturally in downstream code (e.g. `marketing.post.drafted`).
_DEPARTMENTS: tuple[Department, ...] = (
    Department(
        name="cashier",
        repo="lemonade-cashier",
        owns=(
            "deterministic checkout",
            "product matching",
            "cart state",
            "totals",
            "cash tender",
            "change",
            "receipts",
            "cash-in-transit custody",
            "audit/replay",
            "barter records (attendant-approved)",
        ),
        consumes=(
            "inventory.created",
            "inventory.adjusted",
            "inventory.category.updated",
        ),
        emits=(
            "cashier.transaction.opened",
            "cashier.transaction.line_added",
            "cashier.transaction.line_voided",
            "cashier.transaction.closed",
            "cashier.cit.drop",
            "cashier.cit.pickup",
            "cashier.cit.bag.sealed",
            "cashier.cit.bag.handoff",
            "cashier.cit.bag.received",
            "cashier.barter.recorded",
        ),
        agents=("supervisor", "parser"),
        requires_owner_approval_for=(),
        reads=("cashier.", "inventory.", "store.", "audit."),
        writes=("cashier.",),
        proposals=(),
    ),
    Department(
        name="inventory",
        repo="lemonade-inventory",
        owns=(
            "local product catalog",
            "category schema",
            "SKU aliases",
            "stock counts",
            "reorder thresholds",
            "soil product records",
            "zone and shelf metadata",
            "product images and onboarding metadata",
        ),
        consumes=(
            "cashier.transaction.closed",
            "supplier.order.received",
        ),
        emits=(
            "inventory.created",
            "inventory.adjusted",
            "inventory.counted",
            "inventory.low_stock",
            "inventory.category.updated",
        ),
        agents=("onboarder",),
        requires_owner_approval_for=("delete_product", "rename_category"),
        reads=("inventory.", "cashier.", "supplier.", "store.", "audit."),
        writes=("inventory.",),
        proposals=("supplier.po.suggest",),
    ),
    Department(
        name="accounting",
        repo="lemonade-accounting",
        owns=(
            "daily cash close",
            "cash drawer reconciliation",
            "CIT reconciliation",
            "barter ledger",
            "expense records",
            "supplier cost records",
            "category sales summaries",
            "soil sales summaries",
            "tax summary exports",
            "CSV exports for accountant",
        ),
        consumes=(
            "cashier.transaction.closed",
            "cashier.cit.bag.received",
            "cashier.barter.recorded",
            "supplier.order.received",
            "inventory.adjusted",
        ),
        emits=(
            "accounting.daily_close",
            "accounting.cash_reconciled",
            "accounting.barter_recorded",
            "accounting.expense_recorded",
            "accounting.export.created",
        ),
        agents=("closer",),
        requires_owner_approval_for=("export", "tax_filing_summary"),
        reads=(
            "cashier.",
            "supplier.",
            "inventory.",
            "store.",
            "audit.",
        ),
        writes=("accounting.",),
        proposals=(),
    ),
    Department(
        name="marketeer",
        repo="lemonade-marketeer",
        namespace="marketing",
        owns=(
            "organic social post drafts",
            "promotion calendar",
            "product copy",
            "website content drafts",
            "campaign ideas",
            "social posting checklist",
        ),
        consumes=(
            "inventory.created",
            "inventory.category.updated",
            "accounting.daily_close",
        ),
        emits=(
            "marketing.post.drafted",
            "marketing.post.approved",
            "marketing.site_update.drafted",
            "marketing.campaign.created",
        ),
        agents=("drafter",),
        # `publish` covers public posting; `ad_spend` covers any paid
        # promotion. Both must stay owner-gated in v0.1.
        requires_owner_approval_for=("publish", "ad_spend"),
        reads=("inventory.", "accounting.", "store.", "audit."),
        writes=("marketing.",),
        proposals=("site.change.draft",),
    ),
    Department(
        name="supplier",
        repo="lemonade-supplier",
        owns=(
            "supplier records",
            "supplier catalog references",
            "purchase order drafts",
            "reorder suggestions",
            "received inventory records",
        ),
        consumes=(
            "inventory.low_stock",
            "accounting.expense_recorded",
        ),
        emits=(
            "supplier.po.drafted",
            "supplier.order.received",
            "supplier.price.updated",
        ),
        agents=("buyer",),
        requires_owner_approval_for=("po_submit",),
        reads=("inventory.", "accounting.", "store.", "audit."),
        writes=("supplier.",),
        proposals=(),
    ),
    Department(
        name="reports",
        repo="lemonade-reports",
        owns=(
            "end-of-day owner summary",
            "weekly owner digest",
            "slow movers report",
            "category revenue report",
            "cash and CIT exceptions report",
            "inventory risk report",
            "marketing activity summary",
        ),
        consumes=(
            "cashier.transaction.closed",
            "accounting.daily_close",
            "inventory.low_stock",
            "marketing.post.approved",
            "supplier.order.received",
        ),
        emits=(
            "reports.daily",
            "reports.weekly",
            "reports.exception",
        ),
        agents=("summarizer",),
        requires_owner_approval_for=(),
        reads=(
            "cashier.",
            "accounting.",
            "inventory.",
            "marketing.",
            "supplier.",
            "store.",
            "audit.",
        ),
        writes=("reports.",),
        proposals=(),
    ),
    Department(
        name="site",
        repo="lemonade-site",
        owns=(
            "public website",
            "static pages",
            "product/category pages",
            "soil availability page",
            "store hours",
            "contact instructions",
            "privacy and local-data statement",
            "Cloudflare deployment guide",
        ),
        consumes=(
            "marketing.post.approved",
            "marketing.site_update.drafted",
        ),
        emits=(
            "site.change.drafted",
            "site.change.approved",
            "site.deploy.requested",
            "site.deploy.completed",
        ),
        agents=("publisher",),
        requires_owner_approval_for=("deploy", "publish_change"),
        reads=("marketing.", "inventory.", "store.", "audit."),
        writes=("site.",),
        proposals=(),
    ),
)


def registry() -> dict[str, Department]:
    """Return the v0.1 department registry as `{name: Department}`.

    Returned dict is a fresh copy; callers may mutate it without
    leaking into other consumers. The underlying `Department` objects
    are frozen.
    """
    return {dept.name: dept for dept in _DEPARTMENTS}
