"""
Script to create a clean, high-resolution UI screenshot of GigPitch AI
Dimensions: 1280x820
"""
from PIL import Image, ImageDraw, ImageFont
import os


def create_app_screenshot(output_path="assets/screenshot.png"):
    W, H = 1280, 820
    img = Image.new("RGBA", (W, H), (7, 7, 20, 255))
    draw = ImageDraw.Draw(img)

    # 1. Base gradient
    for y in range(H):
        r = int(7 + (13 - 7) * (y / H))
        g = int(7 + (13 - 7) * (y / H))
        b = int(20 + (33 - 20) * (y / H))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Glowing orbs
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for cx, cy, rad, (or_r, or_g, or_b) in [
        (1100, 100, 280, (245, 183, 38)),
        (100, 700, 260, (229, 57, 39)),
        (600, 300, 240, (139, 178, 222)),
    ]:
        for r_step in range(rad, 0, -4):
            alpha = int(22 * (1.0 - (r_step / rad) ** 1.5))
            gdraw.ellipse([cx - r_step, cy - r_step, cx + r_step, cy + r_step], fill=(or_r, or_g, or_b, alpha))

    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    def load_font(fnames, size):
        for fn in fnames:
            for d in ["C:/Windows/Fonts", "/usr/share/fonts/truetype", "."]:
                fp = os.path.join(d, fn)
                if os.path.isfile(fp):
                    try:
                        return ImageFont.truetype(fp, size)
                    except Exception:
                        pass
        return ImageFont.load_default(size=size)

    f_title = load_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 22)
    f_hero = load_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 36)
    f_sub = load_font(["arial.ttf", "SegoeUI.ttf"], 16)
    f_card_title = load_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 16)
    f_label = load_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 12)
    f_body = load_font(["consola.ttf", "arial.ttf"], 13)
    f_tag = load_font(["arialbd.ttf", "SegoeUI-Bold.ttf"], 12)

    # 3. Top Nav Bar
    draw.rectangle([0, 0, W, 60], fill=(10, 10, 26, 230), outline=(255, 255, 255, 25))
    draw.rounded_rectangle([40, 12, 76, 48], radius=8, fill=(245, 183, 38, 240))
    draw.text((88, 18), "GigPitch", font=f_title, fill=(255, 255, 255))
    draw.rounded_rectangle([180, 20, 208, 38], radius=9, fill=(245, 183, 38, 40), outline=(245, 183, 38, 120))
    draw.text((187, 23), "AI", font=f_tag, fill=(245, 183, 38))

    # Right side status
    draw.rounded_rectangle([1020, 16, 1240, 44], radius=14, fill=(255, 255, 255, 12), outline=(255, 255, 255, 30))
    draw.ellipse([1034, 26, 1042, 34], fill=(16, 185, 129))
    draw.text((1052, 23), "Qwen 3.8 (Open-Weight)", font=f_tag, fill=(203, 213, 225))

    # 4. Hero Section
    draw.rounded_rectangle([480, 85, 800, 110], radius=12, fill=(245, 183, 38, 25), outline=(245, 183, 38, 80))
    draw.text((500, 90), "Hacktoberfest 2026 · Week 2: Side Hustle", font=f_tag, fill=(245, 183, 38))

    draw.text((410, 125), "Win More Gigs. Write 10x Faster.", font=f_hero, fill=(255, 255, 255))
    draw.text((415, 175), "Paste client job descriptions, pick your style, and stream winning proposals in seconds.", font=f_sub, fill=(148, 163, 184))

    # Presets row
    px = 440
    py = 205
    draw.text((px, py + 3), "Quick Presets:", font=f_tag, fill=(100, 116, 139))
    for ptext in ["React Dashboard", "Mobile MVP", "Python Automation"]:
        pw = int(draw.textlength(ptext, font=f_tag)) + 24
        draw.rounded_rectangle([px + 90, py, px + 90 + pw, py + 24], radius=12, fill=(255, 255, 255, 10), outline=(255, 255, 255, 30))
        draw.text((px + 102, py + 4), ptext, font=f_tag, fill=(203, 213, 225))
        px += pw + 10

    # 5. Grid Panels
    card_y = 250
    card_h = 530

    # LEFT CARD: INPUT FORM
    draw.rounded_rectangle([40, card_y, 620, card_y + card_h], radius=16, fill=(13, 13, 33, 220), outline=(255, 255, 255, 25))
    draw.text((60, card_y + 20), "1. Job & Profile Details", font=f_card_title, fill=(255, 255, 255))

    # Job input textarea simulation
    draw.text((60, card_y + 60), "CLIENT JOB POSTING", font=f_label, fill=(148, 163, 184))
    draw.rounded_rectangle([60, card_y + 80, 600, card_y + 210], radius=10, fill=(7, 7, 20, 240), outline=(255, 255, 255, 25))
    job_lines = [
        "Looking for a Senior React/Next.js developer to rebuild our B2B SaaS dashboard.",
        "- Convert complex Figma designs into responsive Tailwind components",
        "- Connect to 5+ REST API endpoints with real-time data refreshes",
        "- Sub-second page load performance and clean state management",
        "Budget: $1,500. Timeline: 10-14 days."
    ]
    for i, line in enumerate(job_lines):
        draw.text((75, card_y + 92 + i * 22), line, font=f_body, fill=(203, 213, 225))

    # Skills input textarea simulation
    draw.text((60, card_y + 225), "YOUR SKILLS & VALUE PROPOSITION", font=f_label, fill=(148, 163, 184))
    draw.rounded_rectangle([60, card_y + 245, 600, card_y + 345], radius=10, fill=(7, 7, 20, 240), outline=(255, 255, 255, 25))
    skill_lines = [
        "Full-Stack React & Next.js specialist with 4+ years experience. Expert in Tailwind CSS,",
        "TanStack Query, TypeScript, and high-performance charts. Built 12+ production dashboards",
        "with 5-star ratings and sub-100ms load times."
    ]
    for i, line in enumerate(skill_lines):
        draw.text((75, card_y + 258 + i * 22), line, font=f_body, fill=(203, 213, 225))

    # Tone Selector
    draw.text((60, card_y + 360), "PROPOSAL TONE", font=f_label, fill=(148, 163, 184))
    tx = 60
    for t_name, active in [("Professional", True), ("Friendly", False), ("High-Impact", False)]:
        tw = 170
        t_bg = (245, 183, 38, 35) if active else (255, 255, 255, 8)
        t_border = (245, 183, 38, 180) if active else (255, 255, 255, 25)
        t_col = (245, 183, 38) if active else (148, 163, 184)
        draw.rounded_rectangle([tx, card_y + 380, tx + tw, card_y + 420], radius=10, fill=t_bg, outline=t_border)
        draw.text((tx + 40, card_y + 392), t_name, font=f_tag, fill=t_col)
        tx += tw + 15

    # Generate Button
    draw.rounded_rectangle([60, card_y + 450, 600, card_y + 505], radius=12, fill=(245, 183, 38, 255))
    draw.text((230, card_y + 468), "Generate Winning Proposal", font=f_card_title, fill=(7, 7, 20))

    # RIGHT CARD: PROPOSAL OUTPUT
    draw.rounded_rectangle([660, card_y, 1240, card_y + card_h], radius=16, fill=(13, 13, 33, 220), outline=(255, 255, 255, 25))
    draw.text((680, card_y + 20), "2. Tailored Proposal", font=f_card_title, fill=(255, 255, 255))
    draw.text((1110, card_y + 22), "142 words · ~1 min read", font=f_tag, fill=(148, 163, 184))

    # Proposal Box
    draw.rounded_rectangle([680, card_y + 60, 1220, card_y + 440], radius=10, fill=(7, 7, 20, 240), outline=(255, 255, 255, 25))
    prop_lines = [
        "A clunky dashboard kills user engagement faster than missing features.",
        "Building your SaaS analytics so it renders instantly while cleanly orchestrating",
        "five live REST endpoints without blocking the UI thread is the exact problem",
        "I specialize in.",
        "",
        "Over the past three years, I've shipped 12+ production dashboards using React,",
        "Next.js, and Tailwind CSS. I prioritize clean state management, modular component",
        "hierarchies, and sub-100ms UI response times so your team can extend features",
        "long after launch.",
        "",
        "I can have your core layout and initial API wiring ready for review within 4 days.",
        "Are you open to a quick 10-minute sync tomorrow to walk through your Figma specs?"
    ]
    for i, line in enumerate(prop_lines):
        draw.text((698, card_y + 78 + i * 24), line, font=f_body, fill=(226, 232, 240))

    # Output Actions Bar
    draw.rounded_rectangle([680, card_y + 460, 840, card_y + 505], radius=10, fill=(255, 255, 255, 12), outline=(255, 255, 255, 30))
    draw.text((715, card_y + 475), "Copy Proposal", font=f_tag, fill=(255, 255, 255))

    draw.rounded_rectangle([855, card_y + 460, 1025, card_y + 505], radius=10, fill=(245, 183, 38, 25), outline=(245, 183, 38, 120))
    draw.text((885, card_y + 475), "Save to History", font=f_tag, fill=(245, 183, 38))

    draw.rounded_rectangle([1040, card_y + 460, 1220, card_y + 505], radius=10, fill=(255, 255, 255, 12), outline=(255, 255, 255, 30))
    draw.text((1080, card_y + 475), "Regenerate", font=f_tag, fill=(203, 213, 225))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final = img.convert("RGB")
    final.save(output_path, "PNG", quality=95)
    print(f"App screenshot created at {output_path}")


if __name__ == "__main__":
    create_app_screenshot()
