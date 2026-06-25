# Troubleshooting and Recovery

## Missing package in manifest

If install says a required distribution is missing, use `lemonade plan` to view the required distributions and rebuild the USB bundle/LAN mirror with those artifacts.

## Hash mismatch

A hash mismatch means the artifact does not match the manifest. Do not install it. Rebuild the bundle from trusted sources.

## Public URL rejected

Normal store installs must be offline/internal. Replace public URLs with local artifact paths.

## Disable a package

```sh
lemonade disable reports
lemonade enable reports
```

Disable preserves data and records. It is the safe default.

## Restore from backup

Restore the store data directory and package-manager state file together so enabled packages match the local data layout.
