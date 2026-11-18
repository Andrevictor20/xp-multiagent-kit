#!/usr/bin/env python3
"""Tests for scripts/design_search.py (design-intelligence skill)."""

import colorsys
import tempfile
import unittest
from pathlib import Path

from scripts import design_search as ds


def _rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _luminance(hex_color: str) -> float:
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in _rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class DatasetInvariantsTest(unittest.TestCase):
    def test_all_domains_load_non_empty(self):
        for domain in ds.DOMAINS:
            self.assertGreaterEqual(len(ds.load(domain)), 8, domain)

    def test_palettes_respect_kit_locks(self):
        for p in ds.load("palettes"):
            self.assertNotEqual(p["bg"].upper(), "#000000", p["name"])
            self.assertNotEqual(p["text"].upper(), "#000000", p["name"])
            self.assertGreaterEqual(_contrast(p["text"], p["bg"]), 7.0, p["name"])
            _, s, _ = colorsys.rgb_to_hsv(*_rgb(p["accent"]))
            self.assertLess(s, 0.80, p["name"])

    def test_palette_accent_readable_as_ui_component(self):
        for p in ds.load("palettes"):
            self.assertGreaterEqual(_contrast(p["accent"], p["bg"]), 3.0, p["name"])

    def test_products_reference_existing_palettes_and_fonts(self):
        palettes = {p["name"] for p in ds.load("palettes")}
        fonts = {f["name"] for f in ds.load("fonts")}
        for prod in ds.load("products"):
            self.assertIn(prod["palette"], palettes, prod["product"])
            self.assertIn(prod["fonts"], fonts, prod["product"])
            for dial in ("variance", "motion", "density"):
                self.assertIn(int(prod[dial]), range(1, 11))

    def test_no_banned_cliches_recommended(self):
        for prod in ds.load("products"):
            self.assertNotIn("purple glow", prod["style"].lower())


class SearchTest(unittest.TestCase):
    def test_search_ranks_matching_product_first(self):
        hits = ds.search("products", "fintech banking dashboard")
        self.assertEqual(hits[0]["product"], "Fintech dashboard")

    def test_search_no_match_returns_empty(self):
        self.assertEqual(ds.search("products", "zzzqqq"), [])

    def test_search_ux_rules_by_keyword(self):
        hits = ds.search("ux", "touch target mobile")
        self.assertTrue(any("48" in h["do"] for h in hits))


class DesignSystemTest(unittest.TestCase):
    def test_generate_includes_locks_and_dials(self):
        md = ds.generate_design_system("SaaS analytics dashboard")
        self.assertIn("# Design System MASTER", md)
        self.assertIn("DESIGN_VARIANCE", md)
        self.assertIn("100dvh", md)
        self.assertIn("48px", md)
        self.assertIn("radius_inner = max(0, radius_outer - padding)", md)

    def test_generate_unknown_query_falls_back_with_notice(self):
        md = ds.generate_design_system("zzzqqq")
        self.assertIn("No close product match", md)

    def test_persist_writes_master(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = ds.persist("Luxury hotel booking", Path(tmp))
            self.assertEqual(path, Path(tmp) / "design-system" / "MASTER.md")
            self.assertIn("Design System MASTER", path.read_text(encoding="utf-8"))

    def test_main_cli_search_returns_zero(self):
        self.assertEqual(ds.main(["--domain", "charts", "trend over time"]), 0)


class DesignSystemsCatalogTest(unittest.TestCase):
    PLATFORMS = {"web", "react-native", "flutter", "ios", "android", "hybrid"}

    def test_every_system_has_package_license_and_valid_platform(self):
        for s in ds.load("systems"):
            for field in ("package", "license", "customize", "a11y", "keywords"):
                self.assertTrue(s[field].strip(), f"{s['name']}.{field}")
            self.assertIn(s["platform"], self.PLATFORMS, s["name"])

    def test_catalog_covers_existing_kit_routing_map(self):
        names = {s["name"] for s in ds.load("systems")}
        for expected in ("Fluent UI", "Material Web", "Carbon", "Polaris", "Atlaskit",
                         "Primer", "GOV.UK", "USWDS", "shadcn/ui", "Radix Themes"):
            self.assertIn(expected, names)

    def test_search_systems_finds_react_native(self):
        names = [s["name"] for s in ds.search("systems", "react native expo", 5)]
        self.assertTrue(any(n in names for n in ("gluestack-ui", "React Native Paper", "Tamagui")))

    def test_web_design_system_recommends_base_system(self):
        md = ds.generate_design_system("SaaS analytics dashboard")
        self.assertIn("Base system:", md)
        self.assertIn("never ship the default theme", md)


class MobileCatalogTest(unittest.TestCase):
    def test_mobile_ux_platform_values_and_units(self):
        rules = ds.load("mobile")
        for r in rules:
            self.assertIn(r["platform"], ("ios", "android", "both"), r["id"])
        touch = " ".join(r["do"] for r in ds.search("mobile", "touch target", 5))
        self.assertIn("44pt", touch)
        self.assertIn("48dp", touch)

    def test_mobile_apps_reference_existing_palettes_fonts_systems(self):
        palettes = {p["name"] for p in ds.load("palettes")}
        fonts = {f["name"] for f in ds.load("fonts")}
        systems = {s["name"] for s in ds.load("systems")}
        for app in ds.load("mobile-apps"):
            self.assertIn(app["palette"], palettes, app["app"])
            self.assertIn(app["fonts"], fonts, app["app"])
            self.assertIn(app["system"], systems, app["app"])
            self.assertIn(int(app["variance"]), range(1, 11))

    def test_generate_mobile_has_platform_sections(self):
        md = ds.generate_design_system("fitness tracker app", mobile=True)
        for needle in ("# Design System MASTER", "Mobile", "44pt", "48dp",
                       "safe area", "Dynamic Type", "Navigation:", "Base system:"):
            self.assertIn(needle, md)

    def test_mobile_unknown_query_falls_back_with_notice(self):
        self.assertIn("No close app match", ds.generate_design_system("zzzqqq", mobile=True))

    def test_cli_mobile_flag_returns_zero(self):
        self.assertEqual(ds.main(["--mobile", "food delivery app"]), 0)


class SourceVerificationTest(unittest.TestCase):
    def test_every_system_has_status_and_verification_date(self):
        for s in ds.load("systems"):
            self.assertIn(s["status"], ("active", "maintenance"), s["name"])
            self.assertRegex(s["verified"], r"^\d{4}-\d{2}-\d{2}$", s["name"])

    def test_deprecated_polaris_react_package_not_listed(self):
        polaris = next(s for s in ds.load("systems") if s["name"] == "Polaris")
        self.assertNotEqual(polaris["package"].strip(), "@shopify/polaris")
        self.assertIn("web components", polaris["package"].lower())

    def test_material_web_flagged_maintenance(self):
        mw = next(s for s in ds.load("systems") if s["name"] == "Material Web")
        self.assertEqual(mw["status"], "maintenance")

    def test_uswds_license_lists_all_components(self):
        us = next(s for s in ds.load("systems") if s["name"] == "USWDS")
        for part in ("CC0", "Apache-2.0", "OFL"):
            self.assertIn(part, us["license"])

    def test_maintenance_systems_never_auto_recommended(self):
        md = ds.generate_design_system("google material product consumer m3")
        self.assertNotIn("Base system:** Material Web", md)


if __name__ == "__main__":
    unittest.main()
