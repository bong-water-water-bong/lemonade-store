# Agent Safety Policies & Safe Zones

> Safety guidelines, hard rules, owner approval gates, and forbidden development paths for AI agents working in the `lemonade-store` ecosystem.

## Hard Rules

All agent actions and implementations must strictly adhere to the following six engineering laws:

1. **Cash-Only Core**: Absolutely no Stripe, credit card readers, wallets, or third-party payment gateways in the core path. Only cash tender, change, receipts, Cash-in-Transit (CIT) custody, and explicitly approved barter records are allowed.
2. **Cashier is Source of Truth**: The cashier repository is the absolute source of truth for checkout transactions. Downstream departments (accounting, inventory, etc.) *consume* cashier events; they are forbidden from modifying or rewriting closed cashier transactions.
3. **Local-First Operations**: The store must be able to perform daily closes, till reconciliations, and inventory checks offline on a single local workstation (AMD Strix Halo). Network connections are permitted only for syncing the public marketing website to Cloudflare.
4. **The Envelope is the Contract**: Inter-department communication is restricted to the `store.event.v1` schema. Any data sent out-of-band may be silently dropped by consumers.
5. **No Runtime Dependencies**: The core contracts package (`src/lemonade_store/`) imports Python standard library modules only.
6. **Privacy Boundary**: Do not persist or process customer card data, audio recordings, or images anywhere in the suite.

---

## Owner Approval Gates

Agents are helpers, not decision-makers. Any action that has financial, regulatory, or public reach must be gated by explicit human owner approval:

- **Marketing/Social Posts**: The marketeer department must write `marketing.post.drafted` events. Publication is barred until an owner approval event is received.
- **Website Deploys**: Deploying code or assets to Cloudflare Pages must be triggered by an owner-approved publish event.
- **Financial Transfers & Barter**: Any barter transaction or export reconciliation adjustments must go through approval states.

### Envelope Approval Protocol
Approval is managed in the `store.event.v1` envelope via two fields:
- `requires_approval: bool`
- `approved_by: str | None`

**Valid States:**
- **Auto** (`requires_approval = False`, `approved_by = None`): Normal events.
- **Draft** (`requires_approval = True`, `approved_by = None`): Needs review; downstream consumers must not execute.
- **Approved** (`requires_approval = True`, `approved_by = "owner_username"`): Safe to execute.

> [!CAUTION]
> Avoid checking only `requires_approval`. Downstream consumers must check `is_auto()` or `is_approved()` before acting on any event with side effects.

---

## Safe Zones & "Do Not Build" List

To keep agent execution safe, certain features are explicitly out of scope. Under no circumstances should an agent implement:

- **Production Payment Gateways**: Integration of online credit/debit/wallet transaction APIs.
- **Cloud-Dependent Backends**: Making daily store operations require an active internet connection.
- **Customer Identity Tracking**: Databases or tracking mechanisms containing customer PII (names, emails, loyalty data).
- **Self-Modifying Agents**: Code that allows an AI model to rewrite its own execution loop or prompt files.
- **Agent-to-Agent Commerce**: Inter-agent wallet/bidding systems or automated financial transactions.
- **Auto-Posting**: Autonomous social media, email campaigns, or blog publishing without human validation.

---

## Agent Handoff Guidelines

When working as an AI coder:
- **Incremental Steps**: Work in small, testable chunks. Run `make all` at each step.
- **Untrusted Input**: Treat all user payload text as untrusted. Schema validation is the responsibility of the consuming department.
- **No Over-Engineering**: Do not introduce third-party packages or complex design patterns to solve problems that Python's standard library can handle natively.

---

## Related

- [[README]] — project wiki entry point
- [[architecture]] — high-level system view and event envelope
- [[departments]] — department contracts and repository registry
