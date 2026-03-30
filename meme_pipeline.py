"""
Multimodal Meme Generator Pipeline - PROFESSIONAL VERSION
Real-world style memes with speech bubbles, text boxes, watermark,
topic-aware emoji images & symbolic overlays.
"""

import os
import uuid
import textwrap
import requests
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import json
import re
import math
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_CLIENT = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Tone → Visual Theme ───────────────────────────────────────────────────────
TONE_THEMES = {
    "funny": {
        "border":  (255, 215,   0),
        "glow":    (255, 165,   0),
        "bubble":  (255, 255, 255),
        "bubble_text": (20,  20,  20),
        "badge":   "😂 FUNNY",
        "badge_bg":(255, 200,   0),
        "emojis":  ["😂","🤣","💀","🔥","😭"],
    },
    "sarcastic": {
        "border":  (147,   0, 211),
        "glow":    (200,   0, 255),
        "bubble":  (240, 220, 255),
        "bubble_text": (40,   0,  80),
        "badge":   "🙄 SARCASTIC",
        "badge_bg":(147,   0, 211),
        "emojis":  ["🙄","😏","💅","🤌","👀"],
    },
    "relatable": {
        "border":  ( 30, 144, 255),
        "glow":    (  0, 200, 255),
        "bubble":  (220, 240, 255),
        "bubble_text": ( 0,  40,  80),
        "badge":   "💯 RELATABLE",
        "badge_bg":( 30, 144, 255),
        "emojis":  ["💯","😩","🤦","😤","👋"],
    },
    "absurd": {
        "border":  (255,  20, 147),
        "glow":    (255,   0, 100),
        "bubble":  (255, 220, 240),
        "bubble_text": ( 80,   0,  40),
        "badge":   "🤯 ABSURD",
        "badge_bg":(255,  20, 147),
        "emojis":  ["🤪","🦄","🌈","🤯","🎪"],
    },
}
DEFAULT_THEME = TONE_THEMES["funny"]


# ── Emoji PNG downloader (multi-CDN) ─────────────────────────────────────────
def fetch_emoji_image(emoji_char: str, size: int = 64) -> Image.Image | None:
    """
    Download an emoji PNG from multiple open CDNs and return as RGBA PIL Image.
    Falls back gracefully if all sources fail.
    """
    codepoints_dash = "-".join(
        f"{ord(c):x}" for c in emoji_char if ord(c) != 0xFE0F
    )
    codepoints_under = "_".join(
        f"{ord(c):x}" for c in emoji_char if ord(c) != 0xFE0F
    )

    urls = [
        # OpenMoji (MIT, PNG 618px)
        f"https://cdn.jsdelivr.net/npm/openmoji@15.0.0/color/618x618/{codepoints_dash.upper()}.png",
        # Twemoji (MIT, PNG 72px)
        f"https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/{codepoints_dash}.png",
        # Noto Emoji (Apache-2, PNG 128px)
        f"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/128/emoji_u{codepoints_under}.png",
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200 and len(r.content) > 500:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                img = img.resize((size, size), Image.LANCZOS)
                return img
        except Exception:
            continue
    return None


# ── Font loader ───────────────────────────────────────────────────────────────
def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ── Topic-aware symbol drawing ────────────────────────────────────────────────
# Maps topic keywords to a draw function name
TOPIC_SYMBOLS = {
    "mobile":     "draw_mobile",
    "phone":      "draw_mobile",
    "smartphone": "draw_mobile",
    "iphone":     "draw_mobile",
    "android":    "draw_mobile",
    "money":      "draw_money",
    "cash":       "draw_money",
    "dollar":     "draw_money",
    "finance":    "draw_money",
    "salary":     "draw_money",
    "food":       "draw_food",
    "eating":     "draw_food",
    "pizza":      "draw_food",
    "coffee":     "draw_coffee",
    "gaming":     "draw_gamepad",
    "game":       "draw_gamepad",
    "gamer":      "draw_gamepad",
    "music":      "draw_music",
    "song":       "draw_music",
    "coding":     "draw_code",
    "developer":  "draw_code",
    "programmer": "draw_code",
    "code":       "draw_code",
    "love":       "draw_heart",
    "crush":      "draw_heart",
    "relationship":"draw_heart",
    "wifi":       "draw_wifi",
    "internet":   "draw_wifi",
    "car":        "draw_car",
    "driving":    "draw_car",
    "star":       "draw_star",
    "sleep":      "draw_sleep",
    "tired":      "draw_sleep",
    "gym":        "draw_dumbbell",
    "fitness":    "draw_dumbbell",
    "work":       "draw_laptop",
    "office":     "draw_laptop",
    "laptop":     "draw_laptop",
}


def _draw_symbol(draw: ImageDraw.Draw, name: str, cx: int, cy: int,
                 size: int, color: tuple, alpha: int = 200):
    fn = globals().get(name)
    if fn:
        fn(draw, cx, cy, size, color, alpha)


def draw_mobile(draw, cx, cy, size, color, alpha=200):
    w, h = size // 2, size
    x, y = cx - w // 2, cy - h // 2
    r = w // 4
    c = (*color, alpha)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, outline=c, width=3)
    draw.rectangle([x+4, y+8, x+w-4, y+h-16], outline=c, width=2)
    draw.ellipse([cx-4, y+h-12, cx+4, y+h-4], outline=c, width=2)
    draw.ellipse([cx-3, y+3, cx+3, y+9], outline=c, width=2)


def draw_money(draw, cx, cy, size, color, alpha=200):
    r = size // 2
    c = (*color, alpha)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=3)
    s = size // 4
    draw.line([(cx, cy-s*2), (cx, cy+s*2)], fill=c, width=3)
    draw.line([(cx-s, cy-s), (cx+s, cy-s)], fill=c, width=2)
    draw.line([(cx-s, cy),   (cx+s, cy)],   fill=c, width=2)
    draw.line([(cx-s, cy+s), (cx+s, cy+s)], fill=c, width=2)


def draw_heart(draw, cx, cy, size, color, alpha=200):
    s = size // 2
    c = (*color, alpha)
    pts = []
    for t in range(0, 360, 5):
        rad = math.radians(t)
        x = s * (16 * math.sin(rad)**3) / 16
        y = -s * (13*math.cos(rad) - 5*math.cos(2*rad)
                  - 2*math.cos(3*rad) - math.cos(4*rad)) / 16
        pts.append((cx + x, cy + y))
    draw.polygon(pts, outline=c, width=2)


def draw_music(draw, cx, cy, size, color, alpha=200):
    s = size // 2
    c = (*color, alpha)
    draw.line([(cx+s//2, cy-s), (cx+s//2, cy+s//2)], fill=c, width=3)
    draw.arc([cx+s//2, cy-s, cx+s, cy-s//2], start=270, end=90, fill=c, width=2)
    draw.ellipse([cx-s//3, cy+s//4, cx+s//3, cy+s*3//4], outline=c, width=2)


def draw_gamepad(draw, cx, cy, size, color, alpha=200):
    w, h = size, size // 2
    x, y = cx - w // 2, cy - h // 2
    c = (*color, alpha)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=h//3, outline=c, width=2)
    mid_x, mid_y = x + w // 4, cy
    arm = size // 8
    draw.line([(mid_x-arm, mid_y), (mid_x+arm, mid_y)], fill=c, width=2)
    draw.line([(mid_x, mid_y-arm), (mid_x, mid_y+arm)], fill=c, width=2)
    bx, by = x + w * 3 // 4, cy
    br = arm // 2
    for dx, dy in [(0, -arm), (arm, 0), (0, arm), (-arm, 0)]:
        draw.ellipse([bx+dx-br, by+dy-br, bx+dx+br, by+dy+br], outline=c, width=2)


def draw_coffee(draw, cx, cy, size, color, alpha=200):
    w, h = size // 2, size * 2 // 3
    x, y = cx - w // 2, cy - h // 2
    c = (*color, alpha)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=4, outline=c, width=2)
    draw.arc([x+w, y+h//4, x+w+w//3, y+h*3//4], start=270, end=90, fill=c, width=2)
    for sx in [-w//4, 0, w//4]:
        draw.arc([cx+sx-3, y-size//3, cx+sx+3, y-2], start=200, end=340, fill=c, width=1)


def draw_wifi(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    for i, r in enumerate([size//2, size//3, size//5]):
        draw.arc([cx-r, cy-r, cx+r, cy+r], start=210, end=330, fill=c, width=3-i)
    draw.ellipse([cx-4, cy+size//6, cx+4, cy+size//6+8], fill=c)


def draw_code(draw, cx, cy, size, color, alpha=200):
    s = size // 2
    c = (*color, alpha)
    draw.line([(cx-s, cy-s//2), (cx-s*3//2, cy), (cx-s, cy+s//2)], fill=c, width=3)
    draw.line([(cx+s, cy-s//2), (cx+s*3//2, cy), (cx+s, cy+s//2)], fill=c, width=3)
    draw.line([(cx+s//3, cy-s*2//3), (cx-s//3, cy+s*2//3)], fill=c, width=3)


def draw_food(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    s = size // 2
    draw.line([(cx-s//2, cy-s), (cx-s//2, cy+s)], fill=c, width=3)
    draw.line([(cx+s//2, cy-s), (cx+s//2, cy+s)], fill=c, width=3)
    draw.line([(cx-s//2, cy),   (cx+s//2, cy)],   fill=c, width=2)


def draw_star(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    pts = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = size // 2 if i % 2 == 0 else size // 4
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, outline=c, width=2)


def draw_sleep(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    for i, (ox, oy, sz) in enumerate([(0,0,size//2),(size//3,-size//3,size//3),(size*2//3,-size*2//3,size//4)]):
        draw.text((cx + ox, cy + oy), "Z", font=load_font(sz, True), fill=c)


def draw_dumbbell(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    s = size // 2
    draw.line([(cx-s, cy), (cx+s, cy)], fill=c, width=4)
    for sx in [-s, s]:
        draw.rectangle([cx+sx-8, cy-s//2, cx+sx+8, cy+s//2], outline=c, width=2)


def draw_car(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    w, h = size, size // 2
    x, y = cx - w // 2, cy - h // 4
    draw.rounded_rectangle([x, y, x+w, y+h], radius=6, outline=c, width=2)
    roof_pts = [(x+w//5, y), (x+w*2//5, y-h//2), (x+w*3//4, y-h//2), (x+w*9//10, y)]
    draw.polygon(roof_pts, outline=c, width=2)
    wr = h // 3
    for wx in [x + w//4, x + w*3//4]:
        draw.ellipse([wx-wr, y+h-wr, wx+wr, y+h+wr], outline=c, width=2)


def draw_laptop(draw, cx, cy, size, color, alpha=200):
    c = (*color, alpha)
    w, h = size, size * 2 // 3
    x, y = cx - w // 2, cy - h // 2
    draw.rounded_rectangle([x, y, x+w, y+h*2//3], radius=4, outline=c, width=2)
    draw.rectangle([x+4, y+4, x+w-4, y+h*2//3-4], outline=c, width=1)
    draw.rounded_rectangle([x-w//10, y+h*2//3, x+w+w//10, y+h], radius=3, outline=c, width=2)


class MemePipeline:

    # ── STEP 1 & 3 — Groq LLaMA ──────────────────────────────────────────────
    def _call_groq(self, user_prompt: str) -> dict:
        system = f"""You are the FUNNIEST viral meme writer on the internet.
Topic: "{user_prompt}"

Think deeply about the SPECIFIC feelings, situations, and humor around this topic.
Write captions that make people say "OH MY GOD THIS IS SO ME".

Return ONLY valid JSON (no markdown):
{{
  "detected_tone": "<funny|sarcastic|relatable|absurd>",
  "image_generation_prompt": "<vivid photorealistic scene showing {user_prompt}, cinematic, detailed, NO text>",
  "meme_format": "<two_panel|speech_bubble|top_bottom|label_arrows>",
  "captions": [
    {{"top_text": "...", "bottom_text": "...", "score": 0.95, "style": "classic"}},
    {{"top_text": "...", "bottom_text": "...", "score": 0.87, "style": "slang"}},
    {{"top_text": "...", "bottom_text": "...", "score": 0.80, "style": "absurd"}}
  ],
  "selected_caption": {{"top_text": "...", "bottom_text": "..."}},
  "meme_style": "classic",
  "topic_emojis": ["<emoji1>","<emoji2>","<emoji3>","<emoji4>","<emoji5>"],
  "speech_lines": ["<line for person 1>","<line for person 2>"],
  "floating_emojis": ["<emoji_A>","<emoji_B>","<emoji_C>","<emoji_D>","<emoji_E>","<emoji_F>"]
}}

STRICT RULES:
- Every word MUST relate to "{user_prompt}"
- Use formats: 'When you...', 'Nobody: / Me:', 'POV:', 'That moment when...'
- Top = setup, Bottom = punchline
- MAX 7 words per line
- speech_lines: 2 short funny speech bubble texts related to the topic
- topic_emojis: 5 emojis DIRECTLY related to "{user_prompt}" (e.g. for mobile: 📱,📲,🔋,📶,🤳)
- floating_emojis: 6 emojis that visually represent "{user_prompt}" context — these will be scattered as images around the meme
- NEVER use generic unrelated words"""

        resp = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return only raw JSON. No markdown. No explanation."},
                {"role": "user",   "content": system}
            ],
            max_tokens=1200,
            temperature=0.92,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|^```\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)

    # ── STEP 2 — Pollinations Image ───────────────────────────────────────────
    def _generate_image(self, prompt: str) -> Image.Image:
        try:
            print("[Image Gen] Generating via Pollinations (Flux model)...")
            encoded = urllib.parse.quote(prompt)
            seed    = uuid.uuid4().int % 99999
            url     = (
                f"https://image.pollinations.ai/prompt/{encoded}"
                f"?width=600&height=500&nologo=true&seed={seed}&model=flux"
            )
            r = requests.get(url, timeout=90)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                print("[Image Gen] ✅ Done!")
                return img
            else:
                print(f"[Image Gen] ❌ {r.status_code}")
                return self._placeholder(prompt)
        except Exception as e:
            print(f"[Image Gen] Error: {e}")
            return self._placeholder(prompt)

    def _placeholder(self, prompt: str) -> Image.Image:
        img = Image.new("RGBA", (600, 500))
        px  = img.load()
        for y in range(500):
            for x in range(600):
                px[x, y] = (
                    int((x / 600) * 160 + 40),
                    int((y / 500) * 100 + 60),
                    int(((x+y) / 1100) * 180 + 60),
                    255
                )
        return img.filter(ImageFilter.GaussianBlur(3))

    # ── STEP 4 — Professional Meme Assembly ──────────────────────────────────

    def _enhance_image(self, img: Image.Image) -> Image.Image:
        rgb = img.convert("RGB")
        rgb = ImageEnhance.Contrast(rgb).enhance(1.2)
        rgb = ImageEnhance.Color(rgb).enhance(1.3)
        rgb = ImageEnhance.Sharpness(rgb).enhance(1.3)
        return rgb.convert("RGBA")

    def _draw_speech_bubble(
        self, canvas: Image.Image,
        text: str,
        tip_x: int, tip_y: int,
        direction: str,
        theme: dict,
        font: ImageFont.FreeTypeFont,
    ) -> Image.Image:
        draw  = ImageDraw.Draw(canvas)
        W, H  = canvas.size
        lines = textwrap.wrap(text.upper(), width=22)
        pad   = 14
        lh    = 28
        bw    = max(draw.textbbox((0,0), ln, font=font)[2] for ln in lines) + pad*2
        bh    = len(lines) * lh + pad * 2
        bw    = max(bw, 120)

        if direction == "left":
            bx = max(10, tip_x - 20)
            by = max(10, tip_y - bh - 30)
        else:
            bx = min(W - bw - 10, tip_x - bw + 20)
            by = max(10, tip_y - bh - 30)

        bx2 = bx + bw
        by2 = by + bh

        bubble_layer = Image.new("RGBA", canvas.size, (0,0,0,0))
        bd = ImageDraw.Draw(bubble_layer)

        for s in range(6, 0, -1):
            bd.rounded_rectangle(
                [bx+s, by+s, bx2+s, by2+s],
                radius=16, fill=(0, 0, 0, 30)
            )
        bd.rounded_rectangle(
            [bx, by, bx2, by2],
            radius=16,
            fill=(*theme["bubble"], 230),
            outline=(*theme["border"], 255),
            width=3
        )

        tail_x = bx + bw // 3 if direction == "left" else bx + bw * 2 // 3
        tail_pts = [(tail_x - 10, by2), (tail_x + 10, by2), (tip_x, tip_y)]
        bd.polygon(tail_pts, fill=(*theme["bubble"], 230))
        bd.line([(tail_x - 10, by2), (tip_x, tip_y)], fill=(*theme["border"], 255), width=2)
        bd.line([(tail_x + 10, by2), (tip_x, tip_y)], fill=(*theme["border"], 255), width=2)

        canvas = Image.alpha_composite(canvas, bubble_layer)
        draw2  = ImageDraw.Draw(canvas)

        for i, ln in enumerate(lines):
            bbox = draw2.textbbox((0,0), ln, font=font)
            tw   = bbox[2] - bbox[0]
            tx   = bx + (bw - tw) // 2
            ty   = by + pad + i * lh
            draw2.text((tx+1, ty+1), ln, font=font, fill=(0,0,0,120))
            draw2.text((tx,   ty),   ln, font=font, fill=(*theme["bubble_text"], 255))

        return canvas

    def _draw_top_bottom_text(
        self, img: Image.Image,
        top: str, bottom: str,
        theme: dict
    ) -> Image.Image:
        W, H   = img.size
        draw   = ImageDraw.Draw(img)
        font   = load_font(54, bold=True)
        small  = load_font(42, bold=True)

        def render_text_line(text: str, y: int, f: ImageFont.FreeTypeFont):
            text  = text.upper()
            lines = textwrap.wrap(text, width=20)
            for i, ln in enumerate(lines):
                bbox = draw.textbbox((0,0), ln, font=f)
                tw   = bbox[2] - bbox[0]
                th   = bbox[3] - bbox[1]
                x    = (W - tw) // 2
                ry   = y + i * (th + 8)
                pad  = 8
                backing = Image.new("RGBA", img.size, (0,0,0,0))
                bd = ImageDraw.Draw(backing)
                bd.rounded_rectangle(
                    [x - pad, ry - pad//2, x + tw + pad, ry + th + pad//2],
                    radius=6, fill=(0,0,0,120)
                )
                img.alpha_composite(backing)
                draw2 = ImageDraw.Draw(img)
                for dx in range(-3,4):
                    for dy in range(-3,4):
                        if dx!=0 or dy!=0:
                            draw2.text((x+dx, ry+dy), ln, font=f, fill=(0,0,0,255))
                draw2.text((x, ry), ln, font=f, fill=(255,255,255,255))

        render_text_line(top,    18,      font)
        render_text_line(bottom, H - 90,  font)
        return img

    def _draw_label_arrows(
        self, img: Image.Image,
        top: str, bottom: str,
        theme: dict
    ) -> Image.Image:
        W, H  = img.size
        draw  = ImageDraw.Draw(img)
        font  = load_font(28, bold=True)
        color = theme["border"]

        labels = [
            (top,    W // 4,     H // 3,     "right"),
            (bottom, W * 3 // 4, H * 2 // 3, "left"),
        ]

        for text, px, py, side in labels:
            lines = textwrap.wrap(text.upper(), width=18)
            pad   = 10
            lh    = 30
            bw    = max(draw.textbbox((0,0),l,font=font)[2] for l in lines) + pad*2
            bh    = len(lines)*lh + pad*2

            bx = px + 30 if side == "right" else px - bw - 30
            by  = py - bh // 2
            bx2 = bx + bw
            by2 = by + bh

            box_layer = Image.new("RGBA", img.size, (0,0,0,0))
            bd = ImageDraw.Draw(box_layer)
            bd.rounded_rectangle([bx,by,bx2,by2], radius=10,
                                  fill=(*theme["bubble"],220),
                                  outline=(*color,255), width=2)
            img = Image.alpha_composite(img, box_layer)
            draw = ImageDraw.Draw(img)

            mid_y  = (by + by2) // 2
            arr_x  = bx if side == "right" else bx2
            draw.line([(px,py),(arr_x, mid_y)], fill=(*color,230), width=3)
            ah = 10
            if side == "right":
                draw.polygon([(px,py),(px+ah,py-ah//2),(px+ah,py+ah//2)], fill=(*color,230))
            else:
                draw.polygon([(px,py),(px-ah,py-ah//2),(px-ah,py+ah//2)], fill=(*color,230))

            for i, ln in enumerate(lines):
                bbox = draw.textbbox((0,0),ln,font=font)
                tw   = bbox[2]-bbox[0]
                tx   = bx + (bw-tw)//2
                ty   = by + pad + i*lh
                draw.text((tx+1,ty+1), ln, font=font, fill=(0,0,0,130))
                draw.text((tx,  ty),   ln, font=font, fill=(*theme["bubble_text"],255))

        return img

    def _add_glowing_border(self, img: Image.Image, theme: dict) -> Image.Image:
        W, H = img.size
        draw = ImageDraw.Draw(img)
        bc   = theme["border"]
        gc   = theme["glow"]
        for i in range(8, 0, -1):
            alpha = int(50*(1-i/8))
            draw.rectangle([i*2,i*2,W-i*2,H-i*2], outline=(*gc,alpha), width=2)
        draw.rectangle([4,4,W-4,H-4], outline=(*bc,255), width=4)
        return img

    def _add_watermark(self, img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        W, H = img.size
        font = load_font(18, bold=False)
        text = "made with MemeGen AI"
        bbox = draw.textbbox((0,0), text, font=font)
        tw   = bbox[2]-bbox[0]
        x    = W - tw - 10
        y    = H - 26
        draw.text((x+1, y+1), text, font=font, fill=(0,0,0,160))
        draw.text((x,   y),   text, font=font, fill=(255,255,255,130))
        return img

    def _add_tone_badge(self, img: Image.Image, theme: dict) -> Image.Image:
        draw  = ImageDraw.Draw(img)
        text  = theme["badge"]
        color = theme["badge_bg"]
        font  = load_font(18, bold=True)
        bbox  = draw.textbbox((0,0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        px, py = 12, 12
        bw = px + tw + 24
        bh = py + th + 14
        layer = Image.new("RGBA", img.size, (0,0,0,0))
        ld    = ImageDraw.Draw(layer)
        ld.rounded_rectangle([px,py,bw,bh], radius=10, fill=(*color,210))
        img = Image.alpha_composite(img, layer)
        ImageDraw.Draw(img).text((px+12, py+7), text, font=font, fill=(255,255,255,255))
        return img

    def _add_emoji_accents(self, img: Image.Image, tone_emojis: list, topic_emojis: list) -> Image.Image:
        """Corner emoji accents via system emoji font (fast fallback)."""
        draw = ImageDraw.Draw(img)
        W, H = img.size
        font = None
        for path in ["C:/Windows/Fonts/seguiemj.ttf",
                     "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"]:
            try:
                font = ImageFont.truetype(path, 30)
                break
            except Exception:
                continue
        if font is None:
            return img

        all_em = list(dict.fromkeys(topic_emojis + tone_emojis))[:4]
        spots  = [(W-42, 42), (W-42, H-72), (10, H-72), (10, 42)]
        for i, em in enumerate(all_em):
            ex, ey = spots[i]
            try:
                draw.text((ex+2, ey+2), em, font=font, fill=(0,0,0,100))
                draw.text((ex,   ey),   em, font=font)
            except Exception:
                pass
        return img

    # ── NEW: Floating Real Emoji Image Overlays ───────────────────────────────
    def _add_floating_emoji_images(
        self, img: Image.Image,
        floating_emojis: list,
        topic_emojis: list,
    ) -> Image.Image:
        """
        Download real emoji PNGs (OpenMoji / Twemoji / Noto) and scatter
        them around the meme edges using a smart non-overlapping zone grid.
        Each emoji gets a slight random rotation for natural feel.
        """
        W, H = img.size

        # Combine and deduplicate, pick up to 8
        all_emojis = list(dict.fromkeys(floating_emojis + topic_emojis))[:8]

        # Zone grid: fractions of W,H — avoids center text area
        scatter_zones = [
            (0.02, 0.16,  0.02, 0.20),   # top-left
            (0.82, 0.95,  0.02, 0.20),   # top-right
            (0.02, 0.16,  0.75, 0.92),   # bottom-left
            (0.80, 0.95,  0.75, 0.92),   # bottom-right
            (0.38, 0.55,  0.02, 0.16),   # top-center
            (0.38, 0.55,  0.80, 0.95),   # bottom-center
            (0.02, 0.14,  0.38, 0.62),   # mid-left
            (0.83, 0.95,  0.38, 0.62),   # mid-right
        ]

        rng = random.Random(7)
        em_sizes = [80, 72, 88, 64, 76, 68, 84, 60]

        placed = 0
        for i, emoji_char in enumerate(all_emojis):
            if i >= len(scatter_zones):
                break
            zone = scatter_zones[i]
            em_size = em_sizes[i % len(em_sizes)]

            print(f"[Emoji] Fetching '{emoji_char}' ({em_size}px)...")
            em_img = fetch_emoji_image(emoji_char, size=em_size)
            if em_img is None:
                print(f"[Emoji] ⚠️  Could not fetch '{emoji_char}', skipping.")
                continue

            # Random position within zone
            x1 = int(zone[0] * W)
            x2 = max(x1 + 1, int(zone[1] * W) - em_size)
            y1 = int(zone[2] * H)
            y2 = max(y1 + 1, int(zone[3] * H) - em_size)

            px = rng.randint(x1, x2)
            py = rng.randint(y1, y2)

            # Random rotation ±20°
            angle = rng.randint(-20, 20)
            em_img = em_img.rotate(angle, expand=True, resample=Image.BICUBIC)

            # Subtle drop shadow
            shadow = Image.new("RGBA", em_img.size, (0,0,0,0))
            sdraw  = ImageDraw.Draw(shadow)
            sw, sh = em_img.size
            sdraw.ellipse([sw//4, sh//4, sw*3//4, sh*3//4], fill=(0,0,0,50))
            shadow = shadow.filter(ImageFilter.GaussianBlur(5))

            # Composite onto meme
            try:
                img.paste(shadow, (px + 4, py + 4), shadow)
                img.paste(em_img, (px, py), em_img)
                placed += 1
                print(f"[Emoji] ✅ Placed '{emoji_char}' at ({px},{py})")
            except Exception as e:
                print(f"[Emoji] ⚠️  Paste failed for '{emoji_char}': {e}")

        print(f"[Emoji] 🎉 {placed}/{len(all_emojis)} emoji images placed.")
        return img

    # ── NEW: Drawn Topic Symbols ───────────────────────────────────────────────
    def _add_topic_symbols(
        self, img: Image.Image,
        user_prompt: str,
        theme: dict
    ) -> Image.Image:
        """
        Match prompt keywords → draw small vector symbols (phone, $, heart…)
        at low opacity in the lower margins for extra visual texture.
        """
        prompt_lower = user_prompt.lower()
        matched_fns  = list(dict.fromkeys(
            fn for kw, fn in TOPIC_SYMBOLS.items() if kw in prompt_lower
        ))[:3]

        if not matched_fns:
            return img

        W, H  = img.size
        color = theme["border"]
        draw  = ImageDraw.Draw(img)

        # Place symbols near bottom-edge margins (below text zone)
        positions = [
            (W - 55,  H - 55, 38),
            (45,      H - 55, 34),
            (W // 2,  H - 52, 30),
        ]

        for i, fn_name in enumerate(matched_fns):
            if i >= len(positions):
                break
            cx, cy, sz = positions[i]
            print(f"[Symbol] Drawing '{fn_name}' at ({cx},{cy}) size={sz}")
            try:
                _draw_symbol(draw, fn_name, cx, cy, sz, color, alpha=155)
            except Exception as e:
                print(f"[Symbol] ⚠️  {e}")

        return img

    # ── FULL PIPELINE ─────────────────────────────────────────────────────────
    def run(self, user_prompt: str) -> dict:
        print(f"\n{'='*55}")
        print(f"[Pipeline] Prompt: {user_prompt}")
        print(f"{'='*55}")

        # Step 1 & 3 — Groq
        print("[Step 1&3] Calling Groq LLaMA...")
        ai    = self._call_groq(user_prompt)
        tone  = ai.get("detected_tone", "funny").lower()
        fmt   = ai.get("meme_format", "top_bottom")
        theme = TONE_THEMES.get(tone, DEFAULT_THEME)
        print(f"         ✅ Tone: {tone} | Format: {fmt}")
        print(f"         ✅ Top : {ai['selected_caption']['top_text']}")
        print(f"         ✅ Bot : {ai['selected_caption']['bottom_text']}")
        print(f"         ✅ Topic emojis   : {ai.get('topic_emojis', [])}")
        print(f"         ✅ Floating emojis: {ai.get('floating_emojis', [])}")

        # Step 2 — Image
        print("[Step 2] Generating base image...")
        img = self._generate_image(ai["image_generation_prompt"])

        # Step 4 — Assemble
        print("[Step 4] Assembling professional meme...")
        img  = self._enhance_image(img)
        W, H = img.size
        top    = ai["selected_caption"]["top_text"]
        bot    = ai["selected_caption"]["bottom_text"]
        speech = ai.get("speech_lines", [top, bot])

        # ── 4a: Floating emoji images (BEFORE text so text stays on top)
        print("[Step 4a] Downloading & placing floating emoji images...")
        img = self._add_floating_emoji_images(
            img,
            floating_emojis=ai.get("floating_emojis", []),
            topic_emojis=ai.get("topic_emojis", []),
        )

        # ── 4b: Vector topic symbols
        print("[Step 4b] Drawing topic symbols...")
        img = self._add_topic_symbols(img, user_prompt, theme)

        # ── 4c: Meme text layout
        if fmt == "speech_bubble":
            bubble_font = load_font(24, bold=True)
            img = self._draw_speech_bubble(img, speech[0] if speech else top,
                                           W//4, H//2, "left", theme, bubble_font)
            img = self._draw_speech_bubble(img, speech[1] if len(speech)>1 else bot,
                                           W*3//4, H//3, "right", theme, bubble_font)
        elif fmt == "label_arrows":
            img = self._draw_label_arrows(img, top, bot, theme)
        else:
            img = self._draw_top_bottom_text(img, top, bot, theme)

        # ── Polish
        img = self._add_glowing_border(img, theme)
        img = self._add_tone_badge(img, theme)
        img = self._add_emoji_accents(img,
                                      theme["emojis"],
                                      ai.get("topic_emojis", ["🔥","💯","😂"]))
        img = self._add_watermark(img)

        # Save
        os.makedirs("output", exist_ok=True)
        filename = f"meme_{uuid.uuid4().hex[:8]}.png"
        out_path = os.path.join("output", filename)
        img.convert("RGB").save(out_path, quality=95)
        print(f"[Step 4] ✅ Saved: {out_path}")
        print(f"{'='*55}\n")

        return {
            "user_prompt":             user_prompt,
            "detected_tone":           tone,
            "image_generation_prompt": ai.get("image_generation_prompt"),
            "captions":                ai.get("captions"),
            "selected_caption":        ai.get("selected_caption"),
            "meme_style":              ai.get("meme_style"),
            "final_meme_url":          f"/output/{filename}",
        }