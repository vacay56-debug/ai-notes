# -*- coding: utf-8 -*-
"""產生 PWA 圖示：深色底 + 暖橘圓角方塊 + 白色 AI 字樣。"""
import os
from PIL import Image, ImageDraw, ImageFont

os.chdir(r"C:\Users\USER\Desktop\AI")
os.makedirs("icons", exist_ok=True)

BG = (180, 83, 10)        # --accent #b4530a
FG = (255, 255, 255)
DARK = (31, 31, 29)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
]


def font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_mark(size, pad_ratio, radius_ratio, bleed):
    """bleed=True -> 背景滿版（maskable）；False -> 圓角方塊 + 透明外圍。"""
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if bleed:
        d.rectangle([0, 0, s, s], fill=BG)
        box_pad = int(s * pad_ratio)
    else:
        box_pad = int(s * pad_ratio)
        r = int(s * radius_ratio)
        d.rounded_rectangle([box_pad, box_pad, s - box_pad, s - box_pad], radius=r, fill=BG)

    inner = s - box_pad * 2
    f = font(int(inner * 0.46))
    text = "AI"
    l, t, r_, b = d.textbbox((0, 0), text, font=f)
    d.text(((s - (r_ - l)) / 2 - l, (s - (b - t)) / 2 - t - inner * 0.06), text, font=f, fill=FG)

    # 底線裝飾，呼應「筆記」
    bar_w = int(inner * 0.34)
    bar_h = max(2, int(inner * 0.045))
    by = int(s / 2 + inner * 0.24)
    d.rounded_rectangle(
        [(s - bar_w) // 2, by, (s + bar_w) // 2, by + bar_h],
        radius=bar_h // 2, fill=(255, 255, 255, 200),
    )
    return img.resize((size, size), Image.LANCZOS)


def flatten(img, bg):
    out = Image.new("RGB", img.size, bg)
    out.paste(img, mask=img.split()[3])
    return out


made = []

for size in (192, 512):
    p = "icons/icon-%d.png" % size
    draw_mark(size, 0.06, 0.22, False).save(p)
    made.append(p)

for size in (192, 512):
    p = "icons/maskable-%d.png" % size
    draw_mark(size, 0.20, 0.0, True).save(p)
    made.append(p)

# iOS：不支援透明，直接滿版
flatten(draw_mark(180, 0.16, 0.0, True), BG).save("icons/apple-touch-icon.png")
made.append("icons/apple-touch-icon.png")

# 瀏覽器分頁小圖
flatten(draw_mark(32, 0.0, 0.0, True), BG).save("icons/favicon-32.png")
made.append("icons/favicon-32.png")

for p in made:
    print(p, os.path.getsize(p), "bytes")
