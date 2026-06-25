# Operator Guide

This guide is for store owners, managers, and attendants using the internal Lemonade POS/admin website.

## What Lemonade installs

Lemonade starts with `lemonade-store`, the base contract package. The package manager then enables department packages and agent packages selected by the owner/admin.

The normal store profile installs cashier, inventory, accounting, reports, and security. This supports daily sales, stock checks, daily close, owner reports, and local policy checks without public internet.

## What attendants can do

Attendants can use the POS and read operator help docs. They cannot install packages, change agents, export sensitive records, publish public content, or approve owner-gated actions.

## What owners/admins can do

Owners and delegated admins can open the internal admin wizard to install, disable, update, or roll back packages from a USB bundle or LAN mirror. Owner approval gates still apply to financial exports, public publishing, purchase-order submission, and sensitive security reports.

## Public internet rule

The POS and internal admin website are for localhost/LAN use only. Normal package installs do not use public package URLs.
