# Lemonade Package Manager

The Lemonade package manager is the internal-only, offline-first way to turn a base `lemonade-store` install into a working store suite.

It is designed for a cash-only POS and internal website. It does not install from the public internet during normal store operation. Packages come from one of two trusted local sources:

1. a USB/offline bundle copied onto the workstation, or
2. a LAN-only mirror such as an owner-controlled NAS.

`lemonade-store` owns the package-manager engine and CLI. The dedicated `lemonade-admin` package owns the internal web wizard and local Help Center. Developer details are separated from operator/admin docs.

## Default profile

The recommended default profile is **Store operations**:

- cashier
- inventory
- accounting
- reports
- security

Marketing and public-site packages are optional and disabled by default.

## Commands

```sh
lemonade build-bundle --wheels ./wheels --out ./lemonade-bundle.toml --suite-version 0.1.0 --source usb
lemonade list
lemonade plan --profile store-operations
lemonade install --profile store-operations --manifest /media/usb/lemonade-bundle.toml --key /path/to/bundle.key
lemonade status
lemonade uninstall-plan reports
lemonade disable reports
lemonade enable reports
```

`build-bundle` is the maintainer side (assemble an offline bundle from wheels);
the rest are the operator/admin side (verify, install, and manage from that bundle).

## What is in the complete package now

- `lemonade-store` owns the package-manager engine, CLI, catalog, profiles, offline **bundle building**, bootstrap-wheel manifest support (`lemonade-store`/`lemonade-admin`), manifest validation, artifact hashing, install state, status, enable/disable, and safe uninstall planning.
- A complete, runnable example bundle lives in the [offline-bundle example](https://github.com/bong-water-water-bong/lemonade-store/tree/main/examples/offline-bundle).
- `lemonade-admin` exists as the dedicated internal-only admin/help-center package and uses `lemonade-store` package-manager semantics.
- Full operator/admin/developer docs are included under `docs/package-manager/`.

## Documentation map

- [Operator guide](operator-guide.md)
- [Admin install guide](admin-install-guide.md)
- [Internal access model](internal-access.md)
- [Offline bundles and LAN mirrors](offline-bundles.md)
- [Local Help Center](help-center.md)
- [Department guide](departments.md)
- [Agent guide](agents.md)
- [Troubleshooting and recovery](troubleshooting.md)
- [Security and privacy](security-privacy.md)
- [Developer guide](developer-guide.md)
- [`lemonade-admin` repo split](admin-repo.md)
