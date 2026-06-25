# Offline Bundles and LAN Mirrors

The package manager installs from a local manifest named `lemonade-bundle.toml`.

## Bundle shape

```text
lemonade-bundle/
  lemonade-bundle.toml
  wheels/
    lemonade_cashier-0.1.0-py3-none-any.whl
    lemonade_inventory-0.1.0-py3-none-any.whl
```

## Manifest shape

```toml
manifest_version = "lemonade.bundle.v1"
suite_version = "0.1.0"
source = "usb"
signature = "hmac-sha256:<digest>"

[[packages]]
name = "cashier"
distribution = "lemonade-cashier"
version = "0.1.0"
artifact = "wheels/lemonade_cashier-0.1.0-py3-none-any.whl"
sha256 = "sha256:<artifact digest>"
```

## Security rules

- Public `http://` and `https://` artifact URLs are rejected.
- Every artifact hash must match the manifest.
- The manifest carries a signature field.
- Unsigned/developer placeholder bundles are for development only, not normal store operation.

## LAN mirrors

A LAN mirror uses the same manifest and artifacts but stores them on an internal NAS or local server. Treat it like a USB bundle with easier updates.
