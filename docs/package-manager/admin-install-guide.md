# Admin Install Guide

This guide is for the owner or trusted admin setting up a store workstation.

## First install

1. Install Python 3.11 or newer.
2. Install `lemonade-store` from the prepared local bundle or repo checkout.
3. Insert the USB bundle or mount the LAN mirror.
4. Review available choices:

   ```sh
   lemonade list
   lemonade plan --profile store-operations
   ```

5. Install the recommended internal store profile:

   ```sh
   lemonade install --profile store-operations --manifest /path/to/lemonade-bundle.toml
   ```

6. Install `lemonade-admin` when its bundle is present to start the internal web wizard and Help Center.

## Profiles

- `pos-only`: cashier only.
- `store-operations`: cashier, inventory, accounting, reports, security.
- `full-suite`: all departments, including marketing/site workflow.
- `full-suite-agents`: all departments plus all agents.

## Custom installs

Use `--profile none` to start from cashier only, then add choices:

```sh
lemonade plan --profile none --department inventory --agent onboarder
lemonade install --profile none --department inventory --agent onboarder --manifest /path/to/lemonade-bundle.toml
```

## Disable, status, and uninstall planning

The first package-manager version supports status, disable/enable, and a safe uninstall plan:

```sh
lemonade status
lemonade disable reports
lemonade enable reports
lemonade uninstall-plan reports
```

`uninstall-plan` does not delete data. It prints the guarded sequence an admin should follow: disable, create rollback record, remove package code, and preserve the package data directory. Full code uninstall automation is reserved for the next implementation pass because package removal needs careful backup and environment handling.
