# -*- coding: utf-8 -*-
"""Генерирует иконки: адаптивные слои для Android, иконки для сайта и Play Market.

Рисуем с восьмикратным запасом и уменьшаем по Ланцошу — края получаются чистыми
даже на 48 пикселях. Штанга держится внутри безопасной зоны, чтобы круглая маска
лаунчера не срезала блины.
"""
import io
import os
from PIL import Image, ImageDraw

SS = 8                      # кратность сглаживания
TOP = (0xE6, 0x92, 0x42)    # янтарь
BOT = (0x9E, 0x35, 0x2B)    # терракота
INK = (255, 252, 246)

OUT_APP = os.path.dirname(os.path.abspath(__file__))
OUT_ANDROID = os.path.join(os.path.dirname(OUT_APP), 'fullbody-android', 'app', 'src', 'main', 'res')


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def background(px):
    """Диагональная заливка от янтаря к терракоте."""
    S = px * SS
    img = Image.new('RGB', (S, S))
    d = ImageDraw.Draw(img)
    for i in range(S * 2):
        d.line([(i, 0), (0, i)], fill=lerp(TOP, BOT, i / (S * 2 - 1)), width=2)
    return img.resize((px, px), Image.LANCZOS)


def barbell(px, width_ratio, rot=-12):
    """Штанга на прозрачном фоне. width_ratio — доля ширины холста."""
    S = px * SS
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    p = ImageDraw.Draw(lay)
    cy = S / 2
    half = S * width_ratio / 2          # половина ширины штанги
    u = half / 66.0                     # масштаб: половина = 66 условных единиц

    # гриф — потолще, иначе на 48 пикселях теряется
    p.rounded_rectangle([cy - half, cy - 8.5 * u, cy + half, cy + 8.5 * u],
                        radius=8.5 * u, fill=INK)
    # блины: (смещение от центра, полуширина, полувысота)
    for off, w, h in ((61, 7, 27), (42, 9, 45)):
        for sign in (-1, 1):
            x = cy + sign * off * u
            p.rounded_rectangle([x - w * u, cy - h * u, x + w * u, cy + h * u],
                                radius=5.5 * u, fill=INK)
    if rot:
        lay = lay.rotate(rot, resample=Image.BICUBIC, center=(S / 2, S / 2))
    return lay.resize((px, px), Image.LANCZOS)


def composed(px, width_ratio):
    """Готовая квадратная иконка: фон плюс штанга."""
    bg = background(px).convert('RGBA')
    return Image.alpha_composite(bg, barbell(px, width_ratio)).convert('RGB')


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'PNG', optimize=True)


# ── Android: адаптивная иконка ───────────────────────────────────────
# Холст 108dp, безопасная зона — центральные 66dp. Держим штангу в 60%,
# тогда её не срежет ни круглая, ни квадратная маска.
ADAPTIVE = {'mdpi': 108, 'hdpi': 162, 'xhdpi': 216, 'xxhdpi': 324, 'xxxhdpi': 432}
LEGACY = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}

if os.path.isdir(OUT_ANDROID):
    for dpi, px in ADAPTIVE.items():
        save(background(px), f'{OUT_ANDROID}/mipmap-{dpi}/ic_launcher_background.png')
        save(barbell(px, 0.60), f'{OUT_ANDROID}/mipmap-{dpi}/ic_launcher_foreground.png')
    for dpi, px in LEGACY.items():
        save(composed(px, 0.72), f'{OUT_ANDROID}/mipmap-{dpi}/ic_launcher.png')
        save(composed(px, 0.60), f'{OUT_ANDROID}/mipmap-{dpi}/ic_maskable.png')

    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
           '    <background android:drawable="@mipmap/ic_launcher_background" />\n'
           '    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
           '    <monochrome android:drawable="@mipmap/ic_launcher_foreground" />\n'
           '</adaptive-icon>\n')
    for name in ('ic_launcher.xml', 'ic_launcher_round.xml', 'ic_maskable.xml'):
        path = f'{OUT_ANDROID}/mipmap-anydpi-v26/{name}'
        if name == 'ic_maskable.xml' and not os.path.exists(path):
            continue
        io.open(path, 'w', encoding='utf-8', newline='\n').write(xml)
    print('Android: слои и все плотности готовы')

# ── Сайт и Play Market ───────────────────────────────────────────────
save(composed(180, 0.72), f'{OUT_APP}/icon-180.png')      # экран «Домой» на iOS
save(composed(192, 0.72), f'{OUT_APP}/icon-192.png')
save(composed(512, 0.72), f'{OUT_APP}/icon-512.png')
save(composed(512, 0.60), f'{OUT_APP}/icon-512-maskable.png')
save(composed(512, 0.72), f'{OUT_APP}/play-icon-512.png')  # карточка в Play Market
print('Сайт: 180, 192, 512, 512 с безопасной зоной')
