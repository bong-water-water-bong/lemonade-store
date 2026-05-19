"""Tests for store-config loading.

A store config (e.g. the Tie Dye Farms example) wires together a
business identity, the cashier repo it points at, currency, payment
core mode, and barter policy. The loader's job is to refuse invalid
combinations early — before any agent ever boots.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lemonade_store.config import (
    ConfigValidationError,
    StoreConfig,
    load_store_config,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TIE_DYE_DIR = REPO_ROOT / "examples" / "tie-dye-farms"


class TestExampleConfigLoads:
    def test_tie_dye_farms_example_loads(self) -> None:
        cfg = load_store_config(TIE_DYE_DIR / "store.toml")
        assert isinstance(cfg, StoreConfig)
        assert cfg.store_id == "tie-dye-farms"
        assert cfg.business_name == "Tie Dye Farms"
        assert cfg.cashier_repo == "lemonade-cashier"
        assert cfg.payment_core == "cash_only"

    def test_currency_is_configurable_not_guessed(self) -> None:
        cfg = load_store_config(TIE_DYE_DIR / "store.toml")
        # Spec says currency MUST be configurable; example leaves it explicit
        # rather than relying on a default that could quietly become wrong.
        assert cfg.currency in {"USD", "CAD"}

    def test_categories_include_soil(self) -> None:
        cfg = load_store_config(TIE_DYE_DIR / "store.toml")
        assert "soil" in cfg.categories


class TestConfigValidation:
    def test_unknown_payment_core_rejected(self, tmp_path: Path) -> None:
        p = tmp_path / "store.toml"
        p.write_text(
            "\n".join(
                [
                    'store_id = "demo"',
                    'business_name = "Demo"',
                    'suite = "lemonade-store"',
                    'cashier_repo = "lemonade-cashier"',
                    'website_repo = "demo-site"',
                    'currency = "USD"',
                    'payment_core = "stripe"',
                    'barter = "allowed_with_approval"',
                    'cloudflare = "website_only"',
                    'categories = ["vape"]',
                    "",
                ]
            )
        )
        with pytest.raises(ConfigValidationError):
            load_store_config(p)

    def test_unknown_barter_policy_rejected(self, tmp_path: Path) -> None:
        p = tmp_path / "store.toml"
        p.write_text(
            "\n".join(
                [
                    'store_id = "demo"',
                    'business_name = "Demo"',
                    'suite = "lemonade-store"',
                    'cashier_repo = "lemonade-cashier"',
                    'website_repo = "demo-site"',
                    'currency = "USD"',
                    'payment_core = "cash_only"',
                    'barter = "yolo"',
                    'cloudflare = "website_only"',
                    'categories = ["vape"]',
                    "",
                ]
            )
        )
        with pytest.raises(ConfigValidationError):
            load_store_config(p)

    def test_missing_currency_is_rejected_not_guessed(self, tmp_path: Path) -> None:
        p = tmp_path / "store.toml"
        p.write_text(
            "\n".join(
                [
                    'store_id = "demo"',
                    'business_name = "Demo"',
                    'suite = "lemonade-store"',
                    'cashier_repo = "lemonade-cashier"',
                    'website_repo = "demo-site"',
                    'payment_core = "cash_only"',
                    'barter = "allowed_with_approval"',
                    'cloudflare = "website_only"',
                    'categories = ["vape"]',
                    "",
                ]
            )
        )
        with pytest.raises(ConfigValidationError) as exc:
            load_store_config(p)
        assert "currency" in str(exc.value).lower()


class TestKnownDepartmentsResolved:
    def test_example_departments_file_lists_only_known_departments(self) -> None:
        from lemonade_store.config import load_departments_file

        names = load_departments_file(TIE_DYE_DIR / "departments.toml")
        from lemonade_store.departments import KNOWN_DEPARTMENTS

        assert set(names) == KNOWN_DEPARTMENTS
