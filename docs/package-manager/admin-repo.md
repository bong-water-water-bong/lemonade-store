# `lemonade-admin` Repo Split

Create a dedicated `lemonade-admin` repository/package for the internal web/admin system.

## Responsibilities

`lemonade-admin` owns:

- internal POS/admin website shell,
- package-manager web wizard,
- local Help Center,
- owner/admin/attendant role UI,
- package status dashboard,
- backup/restore screens,
- localhost/LAN-only serving.

## Non-responsibilities

`lemonade-admin` does not own the package-manager engine. It calls the `lemonade-store` API and CLI behavior so CLI and web installs resolve the same profiles, dependencies, manifests, and state.

## Why not `lemonade-site`

`lemonade-site` remains the optional public website workflow. Internal POS/admin/help must not be coupled to public hosting.
