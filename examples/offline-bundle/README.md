# Example offline bundle

This directory shows the exact layout an owner/admin copies onto a USB stick
or LAN mirror to install the Lemonade suite **with no internet access**.

```text
offline-bundle/
  lemonade-bundle.toml      # the manifest the package manager reads
  artifacts/
    lemonade_cashier-0.1.0-py3-none-any.whl
    lemonade_inventory-0.1.0-py3-none-any.whl
```

> The `.whl` files here are **placeholders** so the example is self-contained.
> A real bundle contains the actual built wheels for each department/agent.
> (The directory is named `artifacts/` rather than `wheels/` only so the example
> files are not caught by the standard Python `.gitignore`.)

## Rebuild this manifest

The manifest is generated, never hand-edited. After putting real wheels in
`artifacts/`, regenerate the manifest:

```sh
lemonade build-bundle \
  --wheels examples/offline-bundle/artifacts \
  --out examples/offline-bundle/lemonade-bundle.toml \
  --suite-version 0.1.0 \
  --source usb
```

To sign the manifest with a local maintainer key (recommended for real stores):

```sh
lemonade build-bundle \
  --wheels examples/offline-bundle/artifacts \
  --out examples/offline-bundle/lemonade-bundle.toml \
  --suite-version 0.1.0 \
  --source usb \
  --key /path/to/bundle.key
```

## Install from this bundle

```sh
lemonade install \
  --profile store-operations \
  --manifest examples/offline-bundle/lemonade-bundle.toml
```
