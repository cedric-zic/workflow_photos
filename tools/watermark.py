#!/usr/bin/env python3
"""Applique la protection anti-copie sur une image de la galerie.

- Filigrane texte "© Dreymlz" en tuile diagonale, très transparent (lisible
  sur un téléchargement, invisible à l'écran).
- Signature discrète en coin inférieur droit.
- Métadonnées EXIF : Artist, Copyright, ImageDescription (signature numérique).
- Renvoie l'empreinte SHA-256 de l'image protégée.
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIGNATURE = "© Dreymlz"
ARTISTE = "DreyM"
COPYRIGHT = "© Dreymlz — Tous droits réservés"


def _police(taille: int) -> ImageFont.FreeTypeFont:
    for candidat in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(candidat).exists():
            return ImageFont.truetype(candidat, taille)
    return ImageFont.load_default(size=taille)


def proteger_image(src: Path, dst: Path | None = None) -> str:
    dst = dst or src
    img = Image.open(src).convert("RGB")
    w, h = img.size

    tuile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tuile)
    taille = max(14, w // 38)
    police = _police(taille)
    texte = SIGNATURE
    bbox = d.textbbox((0, 0), texte, font=police)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pas_x, pas_y = int(tw * 2.6), int(th * 6)

    couche = Image.new("RGBA", (pas_x, pas_y), (0, 0, 0, 0))
    dc = ImageDraw.Draw(couche)
    dc.text((-bbox[0], -bbox[1]), texte, font=police, fill=(255, 255, 255, 18))
    couche = couche.rotate(-28, expand=True, resample=Image.BICUBIC)

    for y in range(-h, h * 2, pas_y):
        for x in range(-w, w * 2, pas_x):
            tuile.alpha_composite(couche, (x, y))

    coin = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dcoin = ImageDraw.Draw(coin)
    taille_coin = max(12, w // 70)
    police_coin = _police(taille_coin)
    bb = dcoin.textbbox((0, 0), SIGNATURE, font=police_coin)
    dcoin.text(
        (w - (bb[2] - bb[0]) - w // 60, h - (bb[3] - bb[1]) - h // 60),
        SIGNATURE,
        font=police_coin,
        fill=(255, 255, 255, 46),
    )

    protegee = Image.alpha_composite(img.convert("RGBA"), tuile)
    protegee = Image.alpha_composite(protegee, coin).convert("RGB")

    exif = protegee.getexif()
    exif[315] = ARTISTE
    exif[33432] = COPYRIGHT
    exif[270] = f"{SIGNATURE} — {COPYRIGHT}"
    protegee.save(dst, "JPEG", quality=92, exif=exif)

    return hashlib.sha256(dst.read_bytes()).hexdigest()


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: watermark.py <image.jpg> [image2.jpg ...]  (modifie sur place)")
    for arg in sys.argv[1:]:
        p = Path(arg)
        empreinte = proteger_image(p)
        print(f"{p.name}  sha256={empreinte}")


if __name__ == "__main__":
    main()
