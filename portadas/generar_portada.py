import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

SRC = sys.argv[1]
OUT = sys.argv[2]
W, H = 1080, 1920
F = "/usr/share/fonts/opentype/inter/"
def font(name, size): return ImageFont.truetype(F + name, size)

frame = Image.open(SRC).convert("RGB")
# solo la zona de la pantalla (sin la interfaz del iPhone)
screen = frame.crop((0, 330, 947, 1760))

# --- fondo: fotograma ampliado, desenfocado y oscurecido ---
s = max(W / screen.width, H / screen.height)
bg = screen.resize((int(screen.width * s), int(screen.height * s)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = bg.filter(ImageFilter.GaussianBlur(22))
bg = ImageEnhance.Brightness(bg).enhance(0.38)
tint = Image.new("RGB", (W, H), (8, 40, 34))
bg = Image.blend(bg, tint, 0.35)

# degradado negro arriba y abajo
grad = Image.new("L", (1, H))
for y in range(H):
    t = y / H
    a = 0
    if t < 0.42: a = int(235 * (1 - t / 0.42) ** 1.2)
    if t > 0.80: a = int(220 * ((t - 0.80) / 0.20) ** 1.5)
    grad.putpixel((0, y), a)
grad = grad.resize((W, H))
bg = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), bg, grad)
canvas = bg.convert("RGBA")
d = ImageDraw.Draw(canvas)

RED = (255, 59, 59)
WHITE = (255, 255, 255)
M = 70  # margen lateral

# --- etiqueta "SEGÚN UN MEDIO" ---
tag_font = font("Inter-Bold.otf", 38)
tag = "SEGÚN UN MEDIO"
tw = d.textlength(tag, font=tag_font)
tx, ty, th = M, 330, 70
tri = 34
pill_w = int(tw + tri + 28 + 56)
d.rounded_rectangle((tx, ty, tx + pill_w, ty + th), radius=35, outline=RED, width=4, fill=(40, 0, 0, 170))
cx, cy = tx + 28 + tri // 2, ty + th // 2
d.polygon([(cx, cy - 17), (cx - 19, cy + 15), (cx + 19, cy + 15)], fill=RED)
d.text((cx, cy + 3), "!", font=font("Inter-Black.otf", 22), fill=(0, 0, 0), anchor="mm")
d.text((tx + 28 + tri + 16, cy), tag, font=tag_font, fill=WHITE, anchor="lm")

# --- titular ---
def fit(text, fname, max_w, start):
    size = start
    while size > 20:
        f = font(fname, size)
        if d.textlength(text, font=f) <= max_w: return f
        size -= 2
    return font(fname, size)

maxw = W - 2 * M
y = 450
f1 = fit("LOS BOTS DE GROK", "InterDisplay-Black.otf", maxw, 150)
d.text((M, y), "LOS BOTS DE GROK", font=f1, fill=WHITE, anchor="lt")
y += f1.size + 22
f2 = font("InterDisplay-Bold.otf", 74)
for line in ["accedieron a datos", "de empleados"]:
    d.text((M, y), line, font=f2, fill=(230, 236, 234), anchor="lt")
    y += 88
y += 26
f3 = fit("SIN PERMISO", "InterDisplay-Black.otf", maxw - 60, 140)
bw = d.textlength("SIN PERMISO", font=f3)
pad = 26
box = (M - 6, y, M + bw + 2 * pad, y + f3.size + 34)
d.rectangle(box, fill=RED)
d.text((M + pad, y + 14), "SIN PERMISO", font=f3, fill=WHITE, anchor="lt")
y = box[3]

# --- tarjeta con el documento del vídeo (ligeramente girada) ---
doc = frame.crop((100, 893, 885, 1468))
doc = ImageEnhance.Contrast(doc).enhance(1.15)
cw = 800
doc = doc.resize((cw, int(doc.height * cw / doc.width)), Image.LANCZOS)
border = 10
card = Image.new("RGBA", (doc.width + 2 * border, doc.height + 2 * border), (255, 255, 255, 255))
card.paste(doc, (border, border))
card = card.rotate(-4, resample=Image.BICUBIC, expand=True)
shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
sx = (W - card.width) // 2 + 20
sy = y + 50
sh = Image.new("RGBA", card.size, (0, 0, 0, 200))
sh.putalpha(card.split()[3].point(lambda a: 190 if a else 0))
shadow.paste(sh, (sx + 18, sy + 26), sh)
shadow = shadow.filter(ImageFilter.GaussianBlur(26))
canvas = Image.alpha_composite(canvas, shadow)
canvas.paste(card, (sx, sy), card)

canvas.convert("RGB").save(OUT, quality=95)
# vista previa de cómo se ve recortada en la cuadrícula del perfil (3:4)
prev = canvas.convert("RGB").crop((0, (H - 1440) // 2, W, (H - 1440) // 2 + 1440))
prev.save(OUT.replace(".png", "_vista_perfil.png"))
print("ok", y, sy, card.size)
