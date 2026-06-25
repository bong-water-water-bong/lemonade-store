# Security and Privacy

## Hard rules

- Cash-only core.
- No customer card data.
- No customer audio or images by default.
- Cashier is the checkout source of truth.
- Cloud services are not required for store operations.

## Package trust

The package manager rejects public artifact URLs and verifies artifact hashes. Normal store installs should use signed manifests from USB bundles or LAN mirrors.

## Data boundaries

Departments must not read each other's databases directly. Cross-department coordination uses events and approved exports.

## Public website separation

`lemonade-site` is optional and disabled by default. Internal POS/admin/help features belong to `lemonade-admin`, not the public site workflow.
