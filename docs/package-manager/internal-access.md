# Internal Access Model

Lemonade is an internal-only POS/admin system.

## Network boundary

- Default bind target: localhost.
- Optional LAN access: owner/admin chooses the LAN interface explicitly.
- No public internet exposure for POS/admin endpoints.
- Public website work, if enabled later, is a separate owner-approved workflow.

## Roles

### Owner

The owner has full local authority, manages admins, approves financial/public side effects, and can install, update, disable, and roll back packages.

### Admin / manager

A delegated admin can manage package installs and internal docs if the owner allows it. Admins cannot bypass owner approval gates.

### Attendant

An attendant can use the POS and read operator help. Attendants cannot install packages, change agents, export sensitive data, publish content, or approve gated actions.

## Approval gates

Owner approval remains required for exports, public publishing, purchase-order submission, paid promotion, sensitive security sharing, and any future financial/public side effect.
