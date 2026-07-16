"""LinkedIn-shareable badge image generation.

Renders a 1200x630 (standard social-share ratio) PNG certificate for a
contributor's current badge tier — geometric seal graphics rather than
emoji glyphs, so it doesn't depend on a color-emoji font being installed
on the server.
"""

import io
import os

import frappe
from PIL import Image, ImageDraw, ImageFont

from meridian_sim import scoring

APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
LOGO_PATH = os.path.join(APP_PATH, "meridian_sim", "public", "images", "kb-logo.png")

NAVY_DEEP = (10, 30, 60)
NAVY = (20, 38, 74)
GOLD = (196, 160, 65)
GOLD_LIGHT = (232, 197, 107)
WHITE = (255, 255, 255)
MUTED = (180, 195, 220)

TIER_TAGLINE = {
    "contributor": "Contributor",
    "published_contributor": "Published Contributor",
    "bronze_author": "Bronze Author",
    "silver_author": "Silver Author",
    "gold_author": "Gold Author",
    "platinum_author": "Platinum Author",
    "master_designer": "Master Scenario Designer",
}


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def _draw_seal(draw, cx, cy, r, color):
    """A simple rosette: two concentric circles + a ring of small dots."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=6)
    draw.ellipse([cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16], outline=color, width=3)
    import math
    for i in range(24):
        angle = 2 * math.pi * i / 24
        dx, dy = (cx + (r - 4) * math.cos(angle), cy + (r - 4) * math.sin(angle))
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=color)


def render_badge(full_name: str, badge_key: str, badge_label: str, scenarios_authored: int) -> bytes:
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal gradient band
    for x in range(W):
        shade = int(10 + 18 * (x / W))
        draw.line([(x, 0), (x, H)], fill=(shade, shade + 18, shade + 40))
    draw.rectangle([0, 0, W, H], outline=GOLD, width=8)
    draw.rectangle([18, 18, W - 18, H - 18], outline=GOLD, width=2)

    # Logo, top-left
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA").resize((92, 92))
        img.paste(logo, (48, 42), logo)
    except FileNotFoundError:
        pass

    f_kicker = _font("DejaVuSans-Bold.ttf", 20)
    f_tier = _font("DejaVuSans-Bold.ttf", 54)
    f_name = _font("DejaVuSans-Bold.ttf", 40)
    f_sub = _font("DejaVuSans.ttf", 22)
    f_stat = _font("DejaVuSans.ttf", 24)

    draw.text((156, 60), "KNOWLEDGE BRIDGE ACADEMY", font=f_kicker, fill=GOLD_LIGHT)
    draw.text((156, 88), "MERIDIAN SIM · SCENARIO CONTRIBUTOR PROGRAM", font=_font("DejaVuSans.ttf", 15),
              fill=MUTED)

    draw.text((70, 220), badge_label.upper(), font=f_tier, fill=GOLD)
    draw.text((70, 300), full_name, font=f_name, fill=WHITE)
    draw.text((70, 355), "Verified Scenario Contributor", font=f_sub, fill=MUTED)

    stat_text = f"{scenarios_authored} scenario{'s' if scenarios_authored != 1 else ''} published"
    draw.text((70, 460), stat_text, font=f_stat, fill=GOLD_LIGHT)
    draw.text((70, 495), "knowledgebridge.academy", font=_font("DejaVuSans.ttf", 16), fill=MUTED)

    _draw_seal(draw, W - 170, H // 2 + 10, 110, GOLD)
    draw.text((W - 170, H // 2 - 14), "KB", font=_font("DejaVuSans-Bold.ttf", 34), fill=GOLD,
              anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@frappe.whitelist(allow_guest=True)
def linkedin_badge(contributor: str):
    doc = frappe.db.get_value(
        "Contributor", contributor,
        ["full_name", "scenarios_submitted", "scenarios_authored", "role"], as_dict=True,
    )
    if not doc:
        frappe.throw("Unknown contributor", frappe.DoesNotExistError)

    is_master = doc.role == "Core Contributor" and (doc.scenarios_authored or 0) >= 50
    badge = scoring.compute_badge(doc.scenarios_submitted or 0, doc.scenarios_authored or 0, is_master)
    if not badge["key"]:
        frappe.throw("This contributor hasn't earned a badge yet.")

    label = TIER_TAGLINE.get(badge["key"], badge["label"])
    png = render_badge(doc.full_name, badge["key"], label, doc.scenarios_authored or 0)

    frappe.response["type"] = "binary"
    frappe.response["filecontent"] = png
    frappe.response["content_type"] = "image/png"
    slug = doc.full_name.lower().replace(" ", "-")
    frappe.response["filename"] = f"knowledge-bridge-{slug}-{badge['key']}.png"
