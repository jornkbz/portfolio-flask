"""Genera versiones .webp optimizadas de las imágenes estáticas y la imagen Open Graph.

Uso:  python scripts/optimize_images.py
Los originales se conservan (la BD referencia sus rutas); la app sirve el .webp hermano si existe.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'static', 'img')
MAX_WIDTH = 1200
GREEN = (0, 255, 65)


def to_webp(path, max_width=MAX_WIDTH, quality=80, resample=Image.LANCZOS, size=None):
    out = os.path.splitext(path)[0] + '.webp'
    with Image.open(path) as im:
        im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
        if size:
            im = im.resize(size, resample)
        elif im.width > max_width:
            im = im.resize((max_width, round(im.height * max_width / im.width)), resample)
        im.save(out, 'WEBP', quality=quality, method=6)
    print(f"{os.path.basename(path):28} {os.path.getsize(path) // 1024:5} KB -> {os.path.getsize(out) // 1024:4} KB")


def find_font(size):
    for name in ('DejaVuSansMono-Bold.ttf', 'consolab.ttf', 'consola.ttf'):
        for d in ('/usr/share/fonts/truetype/dejavu', r'C:\Windows\Fonts', ''):
            try:
                return ImageFont.truetype(os.path.join(d, name), size)
            except OSError:
                continue
    return ImageFont.load_default(size)


def make_og_image():
    """Imagen 1200x630 para previsualizaciones en LinkedIn, X, WhatsApp..."""
    w, h = 1200, 630
    canvas = Image.new('RGB', (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    # Rejilla tenue tipo terminal
    for x in range(0, w, 30):
        draw.line([(x, 0), (x, h)], fill=(0, 22, 6))
    for y in range(0, h, 30):
        draw.line([(0, y), (w, y)], fill=(0, 22, 6))
    draw.rectangle([20, 20, w - 21, h - 21], outline=GREEN, width=3)

    # Foto de perfil circular
    size = 260
    with Image.open(os.path.join(IMG, 'foto-perfil.jpg')) as p:
        p = p.convert('RGB').resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    px, py = 90, (h - size) // 2
    canvas.paste(p, (px, py), mask)
    draw.ellipse([px - 6, py - 6, px + size + 5, py + size + 5], outline=GREEN, width=5)

    tx = px + size + 70
    draw.text((tx, 180), '> whoami_', font=find_font(34), fill=(0, 170, 45))
    draw.text((tx, 235), 'José Cabezas', font=find_font(64), fill=GREEN)
    draw.text((tx, 310), 'Pulgarín', font=find_font(64), fill=GREEN)
    draw.text((tx, 405), 'SysAdmin · DevOps · Python', font=find_font(32), fill=(220, 255, 225))
    draw.text((tx, 450), 'IA · Ciberseguridad', font=find_font(32), fill=(220, 255, 225))

    out = os.path.join(IMG, 'og-card.png')
    canvas.save(out, 'PNG', optimize=True)
    print(f"og-card.png creada ({os.path.getsize(out) // 1024} KB)")


def main():
    for name in sorted(os.listdir(IMG)):
        path = os.path.join(IMG, name)
        base, ext = os.path.splitext(name)
        if ext.lower() not in ('.png', '.jpg', '.jpeg') or base.startswith(('favicon', 'og-')):
            continue
        if base == 'matrix_pixel_mascot':
            # Se muestra a 45 px: 128 px cubre pantallas de alta densidad
            to_webp(path, size=(128, 128), quality=90)
        else:
            to_webp(path)
    make_og_image()


if __name__ == '__main__':
    sys.exit(main())
