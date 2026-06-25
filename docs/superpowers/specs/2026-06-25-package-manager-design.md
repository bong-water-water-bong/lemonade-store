# Lemonade Offline Package Manager Design

## Goal

Build a complete package-management foundation for Lemonade: after installing `lemonade-store`, an owner/admin can choose departments and agents from an offline USB bundle or LAN mirror, while keeping the POS/admin system internal-only.

## Scope

This design covers the first working package-manager foundation in `lemonade-store` plus documentation and the dedicated `lemonade-admin` repo split. It intentionally keeps `lemonade-store` stdlib-only.

## Architecture

`lemonade-store` owns the package-manager engine and CLI:

- catalog derived from `departments.py`,
- profiles,
- dependency resolution,
- offline manifest validation,
- hash verification,
- install state,
- enable/disable operations.

`lemonade-admin` owns the internal web/admin package:

- package wizard,
- local Help Center,
- role UI,
- internal-only website shell.

`lemonade-site` stays optional public website workflow and is disabled by default.

## Default install profile

The recommended profile is `store-operations`: cashier, inventory, accounting, reports, and security. It excludes marketing and public-site packages by default.

## Package sources

Normal installs use USB/offline bundles or LAN mirrors. Public artifact URLs are rejected. Manifests list exact distributions, versions, local artifact paths, and SHA-256 hashes.

## Access model

Roles are owner, admin/manager, and attendant. Attendants can use POS/help docs but cannot change packages, agents, exports, publishing, or approvals. Admins can manage installs if delegated, but cannot bypass owner approval gates.

## Documentation

Operator/admin docs are separated from developer docs. Markdown is source-of-truth; `lemonade-admin` renders operator/admin docs in the local Help Center.

## Known limitations in this implementation pass

The first implementation supports install, plan, list, enable, and disable. Full code uninstall, environment rollback, and asymmetric manifest signatures are documented as next-pass work because they need environment snapshot and key-management decisions.
