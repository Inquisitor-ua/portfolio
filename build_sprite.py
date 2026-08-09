"""One-off helper: build the inline SVG icon sprite from downloaded brand icons.

Run once to (re)generate config/templates/includes/icon-sprite.html, then delete
or keep for future icon additions.
"""

import re
import sys
from pathlib import Path

SRC = Path(__file__).parent / "_icons"
OUT = Path(__file__).parent / "config" / "templates" / "includes" / "icon-sprite.html"

# simple-icons files (24x24 viewBox), keyed by the slug used in templates.
BRAND = {
    "github": "github.svg",
    "gitlab": "gitlab.svg",
    "x": "x.svg",
    "telegram": "telegram.svg",
    "instagram": "instagram.svg",
    "facebook": "facebook.svg",
    "youtube": "youtube.svg",
    "dribbble": "dribbble.svg",
    "behance": "behance.svg",
    "codepen": "codepen.svg",
    "stackoverflow": "stackoverflow.svg",
    "medium": "medium.svg",
    "devto": "devdotto.svg",
    "mastodon": "mastodon.svg",
    "discord": "discord.svg",
    "bluesky": "bluesky.svg",
    "reddit": "reddit.svg",
}

# bootstrap-icons files (16x16 viewBox -> scaled to 24)
BRAND_16 = {
    "linkedin": "li16.svg",
}

# Hand-authored UI icons on a 24x24 grid, 2px stroke, round caps.
UI = {
    "arrow-up-right": '<path d="M7 17 17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "arrow-right": '<path d="M4 12h16m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "arrow-down": '<path d="M12 4v16m-6-6 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "mail": '<path d="M3 6.5h18v11H3zM3.5 7l8.5 6 8.5-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "phone": '<path d="M6.5 3h3l1.5 4-2 1.5a10 10 0 0 0 6.5 6.5L17 13l4 1.5v3a2.5 2.5 0 0 1-2.8 2.5C10.4 19.2 4.8 13.6 4 5.8A2.5 2.5 0 0 1 6.5 3Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "map-pin": '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="10" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/>',
    "download": '<path d="M12 3v12m-5-5 5 5 5-5M4 20h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="m15.5 15.5 4.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "close": '<path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "sun": '<circle cx="12" cy="12" r="4.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M19.1 4.9l-1.8 1.8M6.7 17.3l-1.8 1.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    "check": '<path d="m5 13 4.5 4.5L19 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "chevron-down": '<path d="m6 10 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "chevron-right": '<path d="m9 6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "code": '<path d="m9 8-5 4 5 4m6-8 5 4-5 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "link": '<path d="M10 14a4 4 0 0 1 0-5.7l2.3-2.3a4 4 0 0 1 5.7 5.7L16.5 13M14 10a4 4 0 0 1 0 5.7l-2.3 2.3a4 4 0 0 1-5.7-5.7L7.5 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "globe": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 12h18M12 3c2.5 2.4 2.5 15.6 0 18M12 3c-2.5 2.4-2.5 15.6 0 18" fill="none" stroke="currentColor" stroke-width="2"/>',
    "calendar": '<rect x="3.5" y="5.5" width="17" height="15" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3.5 10h17M8 3.5V7M16 3.5V7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "briefcase": '<rect x="3" y="7.5" width="18" height="12.5" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 7.5V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1.5M3 13h18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "graduation": '<path d="M12 4 2.5 8.5 12 13l9.5-4.5L12 4Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M6 10.7V16c0 1.7 2.7 3 6 3s6-1.3 6-3v-5.3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "spark": '<path d="M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4L12 3Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M18.5 16.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8.8-2.2Z" fill="currentColor"/>',
    "quote": '<path d="M9.5 6C6.5 7.5 5 10.2 5 14c0 2.5 1.4 4 3.4 4 1.8 0 3.1-1.3 3.1-3.1 0-1.7-1.1-2.9-2.7-2.9-.3 0-.6 0-.8.1.3-1.6 1.3-2.9 3-3.8L9.5 6Zm8 0C14.5 7.5 13 10.2 13 14c0 2.5 1.4 4 3.4 4 1.8 0 3.1-1.3 3.1-3.1 0-1.7-1.1-2.9-2.7-2.9-.3 0-.6 0-.8.1.3-1.6 1.3-2.9 3-3.8L17.5 6Z" fill="currentColor"/>',
    "rss": '<circle cx="6" cy="18" r="2" fill="currentColor"/><path d="M4 11a9 9 0 0 1 9 9M4 5a15 15 0 0 1 15 15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    "external": '<path d="M14 4h6v6M20 4 10 14M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5Zm9 9-9 5-9-5m18 4-9 5-9-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
}


def paths_from(svg_text):
    """Return every <path>/<circle>/<rect> element found in a simple-icons file."""
    body = re.sub(r"<svg[^>]*>|</svg>|<title>.*?</title>", "", svg_text, flags=re.S)
    return body.strip()


def main():
    if not SRC.exists():
        sys.exit(f"Missing {SRC} — download the brand icons first.")

    symbols = []

    for slug, filename in BRAND.items():
        path = SRC / filename
        if not path.exists():
            print(f"  skip {slug}: {filename} not found")
            continue
        inner = paths_from(path.read_text(encoding="utf-8"))
        symbols.append(
            f'<symbol id="icon-{slug}" viewBox="0 0 24 24">{inner}</symbol>'
        )

    for slug, filename in BRAND_16.items():
        path = SRC / filename
        if not path.exists():
            print(f"  skip {slug}: {filename} not found")
            continue
        inner = paths_from(path.read_text(encoding="utf-8"))
        # Scale the 16x16 artwork onto the shared 24x24 grid.
        symbols.append(
            f'<symbol id="icon-{slug}" viewBox="0 0 24 24">'
            f'<g transform="scale(1.5)">{inner}</g></symbol>'
        )

    for slug, inner in UI.items():
        symbols.append(
            f'<symbol id="icon-{slug}" viewBox="0 0 24 24">{inner}</symbol>'
        )

    header = (
        "{% comment %}\n"
        "Inline SVG sprite. Referenced from templates as:\n"
        '    <svg class="icon" aria-hidden="true"><use href="#icon-github"></use></svg>\n'
        "Brand marks come from simple-icons (CC0) and bootstrap-icons (MIT);\n"
        "UI icons are hand-authored on a 24x24 grid.\n"
        "Regenerate with build_sprite.py.\n"
        "{% endcomment %}\n"
    )
    body = "\n".join(symbols)
    OUT.write_text(
        f'{header}<svg xmlns="http://www.w3.org/2000/svg" class="icon-sprite" '
        f'aria-hidden="true" focusable="false" hidden>\n{body}\n</svg>\n',
        encoding="utf-8",
    )
    print(f"Wrote {len(symbols)} symbols to {OUT}")


if __name__ == "__main__":
    main()
