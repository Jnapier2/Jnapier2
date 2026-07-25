#!/usr/bin/env python3
"""Rendered-text adapter for the read-only portfolio audit.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import re
import urllib.parse
from html.parser import HTMLParser

import portfolio_audit as core


class PageTextParser(HTMLParser):
    """Extract visible text and links without executing page content."""

    _IGNORED = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.text_parts: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower_tag = tag.lower()
        if lower_tag in self._IGNORED:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.hrefs.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._IGNORED and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.text_parts.append(data)


def parse_page(document: str, base_url: str) -> tuple[str, set[str]]:
    parser = PageTextParser()
    parser.feed(document)
    parser.close()
    visible_text = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip().lower()
    links = {
        urllib.parse.urljoin(base_url, href).strip().lower()
        for href in parser.hrefs
        if href.strip()
    }
    return visible_text, links


def audit_portfolio_site(audit: core.Audit, manifest: dict[str, object]) -> None:
    url = str(manifest["canonical_portfolio_url"])
    try:
        status, final_url, document = core.request_text(url)
    except Exception as exc:
        audit.add("warning", "portfolio-site", f"Live portfolio check failed: {exc}")
        return

    if status != 200:
        audit.add("warning", "portfolio-site", f"Live portfolio returned HTTP {status}")
    if urllib.parse.urlparse(final_url).scheme != "https":
        audit.add("warning", "portfolio-site", f"Portfolio did not finish on HTTPS: {final_url}")

    visible_text, links = parse_page(document, final_url)
    lower_document = document.lower()
    if "i turn complex systems into trusted ones" not in visible_text:
        audit.add(
            "warning",
            "portfolio-site",
            "Rendered portfolio text did not expose the expected recruiter-facing value statement",
        )

    for value in manifest["forbidden_public_link_fragments"]:
        fragment = str(value).lower()
        if fragment in lower_document or any(fragment in link for link in links):
            audit.add("warning", "portfolio-site", f"Retired public link appears in site HTML: {value}")

    for value in manifest.get("portfolio_privacy_review_fragments", []):
        fragment = str(value).lower()
        present = fragment in visible_text or fragment in lower_document or any(
            fragment in link for link in links
        )
        if present:
            audit.add(
                "warning",
                "portfolio-site",
                f"Manual privacy review remains required for site content: {value}",
            )


def audit_public_profile_render(audit: core.Audit, manifest: dict[str, object]) -> None:
    url = f"https://github.com/{manifest['owner']}"
    try:
        status, final_url, document = core.request_text(url)
    except Exception as exc:
        audit.add("warning", "profile-render", f"Signed-out profile render could not be checked: {exc}")
        return
    if status != 200:
        audit.add("warning", "profile-render", f"Signed-out profile returned HTTP {status}")
        return

    visible_text, links = parse_page(document, final_url)
    lower_document = document.lower()
    if "i turn complex systems into trusted ones" not in visible_text:
        audit.add(
            "warning",
            "profile-render",
            "Signed-out profile text did not expose the current value statement; verify caching manually",
        )
    for value in manifest["forbidden_public_link_fragments"]:
        fragment = str(value).lower()
        if fragment in lower_document or any(fragment in link for link in links):
            audit.add(
                "warning",
                "profile-render",
                f"Signed-out profile still exposes a retired link: {value}",
            )


def main() -> int:
    core.audit_portfolio_site = audit_portfolio_site
    core.audit_public_profile_render = audit_public_profile_render
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
