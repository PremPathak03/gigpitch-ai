"""
GigPitch AI — Python Pillow Thumbnail / Cover Image Generator
Generates a 1000x420 DEV blog cover image tailored for Hacktoberfest 2026 Week 2.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont


def create_thumbnail(output_path="thumbnail/thumbnail.png"):
    width, height = 1000, 420
    img = Image.new("RGBA", (width, height), (7, 7, 20, 255))
    draw = ImageDraw.Draw(img)

    # 1. Base gradient background (deep space navy -> dark slate)
    for y in range(height):
        ratio = y / height
        r = int(7 + (16 - 7) * ratio)
        g = int(7 + (24 - 7) * ratio)
        b = int(20 + (48 - 20) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Glowing ambient light orbs (soft blurred circles)
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    orbs = [
        (850, 70, 240, (245, 183, 38)),     # Ochre/gold glow - top right
        (100, 360, 200, (229, 57, 39)),     # Hacktoberfest red glow - bottom left
        (520, 30, 220, (139, 178, 222)),    # Sky blue glow - top center
    ]

    for cx, cy, rad, (or_r, or_g, or_b) in orbs:
        for r_step in range(rad, 0, -3):
            alpha = int(24 * (1.0 - (r_step / rad) ** 1.6))
            glow_draw.ellipse(
                [cx - r_step, cy - r_step, cx + r_step, cy + r_step],
                fill=(or_r, or_g, or_b, alpha)
            )

    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # 3. Geometric grid & star dust overlay
    for x in range(30, width, 40):
        for y in range(30, height, 40):
            val = int(14 + 10 * math.sin(x * 0.03) * math.cos(y * 0.03))
            if val > 0:
                draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255, val))

    # 4. Font helper with graceful fallbacks
    def get_font(font_names, size):
        search_dirs = [
            "C:/Windows/Fonts",
            "/usr/share/fonts/truetype",
            "/System/Library/Fonts",
            "/Library/Fonts",
            "."
        ]
        for fname in font_names:
            for sdir in search_dirs:
                full_path = os.path.join(sdir, fname)
                if os.path.isfile(full_path):
                    try:
                        return ImageFont.truetype(full_path, size)
                    except Exception:
                        pass
        return ImageFont.load_default(size=size)

    title_font = get_font(["arialbd.ttf", "SegoeUI-Bold.ttf", "DejaVuSans-Bold.ttf"], 56)
    subtitle_font = get_font(["arial.ttf", "SegoeUI.ttf", "DejaVuSans.ttf"], 25)
    badge_font = get_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 14)
    pill_font = get_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 15)
    code_font = get_font(["consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"], 90)

    # 5. Right-side decorative brackets
    draw.text((790, 110), "{ }", font=code_font, fill=(255, 255, 255, 25))

    # 6. Top Badges
    top_badge_y = 55
    # Hacktoberfest 2026 Badge
    draw.rounded_rectangle([60, top_badge_y, 305, top_badge_y + 34], radius=17, fill=(229, 57, 39, 240))
    draw.text((78, top_badge_y + 8), "HACKTOBERFEST 2026", font=badge_font, fill=(255, 255, 255, 255))

    # Side Hustle Badge
    draw.rounded_rectangle([318, top_badge_y, 475, top_badge_y + 34], radius=17, fill=(245, 183, 38, 240))
    draw.text((336, top_badge_y + 8), "SIDE HUSTLE", font=badge_font, fill=(10, 10, 22, 255))

    # 7. Main Title with soft drop shadow
    title_text = "GigPitch AI"
    draw.text((63, 118), title_text, font=title_font, fill=(0, 0, 0, 180))
    draw.text((60, 115), title_text, font=title_font, fill=(245, 183, 38, 255))

    # 8. Subtitle lines
    draw.text((60, 192), "Win more freelance gigs with custom,", font=subtitle_font, fill=(203, 213, 225, 255))
    draw.text((60, 227), "high-converting open-weight AI proposals.", font=subtitle_font, fill=(255, 255, 255, 255))

    # 9. Tech stack pills at the bottom with dark solid backgrounds & colored borders
    pills = [
        ("Open-Weight AI", (245, 183, 38)),
        ("FastAPI", (139, 178, 222)),
        ("Groq LPU", (16, 185, 129)),
        ("Python 3", (255, 220, 100)),
        ("100% Free", (242, 242, 235)),
    ]

    pill_x = 60
    pill_y = 310
    for label, col in pills:
        pw = int(draw.textlength(label, font=pill_font)) + 26
        # Dark pill background
        draw.rounded_rectangle(
            [pill_x, pill_y, pill_x + pw, pill_y + 34],
            radius=8,
            fill=(16, 18, 38, 230),
            outline=(col[0], col[1], col[2], 200),
            width=1
        )
        draw.text((pill_x + 13, pill_y + 8), label, font=pill_font, fill=(col[0], col[1], col[2], 255))
        pill_x += pw + 12

    # 10. Bottom highlight bar (amber -> red gradient)
    for px in range(width):
        frac = px / width
        r_c = int(245 * (1 - frac) + 229 * frac)
        g_c = int(183 * (1 - frac) + 57 * frac)
        b_c = int(38 * (1 - frac) + 39 * frac)
        draw.line([(px, height - 4), (px, height)], fill=(r_c, g_c, b_c, 255))

    # Convert to RGB and save
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    final_img = img.convert("RGB")
    final_img.save(output_path, "PNG", quality=95)
    print(f"Thumbnail successfully generated at {output_path} ({width}x{height})")
    return output_path


if __name__ == "__main__":
    create_thumbnail()
