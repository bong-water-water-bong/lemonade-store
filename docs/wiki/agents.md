# Cashier Safety & Supervisor PIN Policies

This document outlines the cashier safety guidelines and the supervisor PIN entry requirements for transaction overrides, voids, refunds, and discounts.

## Supervisor PIN Thresholds

To prevent fraud, theft, and operational errors, certain financial overrides require a supervisor's PIN. The thresholds are governed by the following constants from `safety/policy.py`:

- **Void Threshold (`DEFAULT_VOID_PIN_THRESHOLD`)**: `Decimal('10.00')`
  - Voids on items or cumulative voids in a single transaction that meet or exceed this value trigger a supervisor PIN prompt.
- **Refund Threshold (`DEFAULT_REFUND_PIN_THRESHOLD`)**: `Decimal('5.00')`
  - Any refund totaling this amount or higher must be approved with a supervisor PIN.
- **Discount Threshold (`DEFAULT_DISCOUNT_PIN_THRESHOLD`)**: `Decimal('3.00')`
  - Individual item or transaction-level discounts equal to or exceeding this threshold require supervisor override.

## Cashier Safety Guidelines

1. **Never Assume Uncertain Products are Correct**: Low-confidence item matches (confidence score below 0.95 or `confidence_floor` not met) must not be silently added to a cart. They require manual cashier/attendant confirmation.
2. **Explicit Attendant Oversight**: Voids, refunds, and discounts that exceed safety limits must not bypass the supervisor verification gate.
3. **No Real Payments**: The system runs entirely in cash-only simulation and must never interface with active payment networks.
4. **Data Privacy Boundary**: Attendant notes, customer voices, and camera feeds must never persist synthetic/unredacted personal identifiable information (PII).
