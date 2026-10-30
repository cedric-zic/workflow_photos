#!/usr/bin/env python3
"""Ajoute un tableau à la galerie, sans toucher au code.

Usage :
    python3 tools/add_tableau.py chemin/vers/ma-photo.jpg

Le script demande le titre, la technique, les dimensions et l'année,
copie la photo dans images/, applique le filigrane © Dreymlz et les
métadonnées de copyright, puis ajoute l'œuvre à galerie.json.
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from watermark import proteger_image, ARTISTE, COPYRIGHT

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_IMAGES = RACINE / "images"
GALERIE = RACINE / "galerie.json"


def demander(question: str, defaut: str = "") -> str:
    saisie = input(f"{question} [{defaut}] : ").strip()
    return saisie or defaut


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python3 tools/add_tableau.py <fichier-image.jpg>")
        sys.exit(1)

    source = Path(sys.argv[1])
    if not source.exists():
        sys.exit(f"Fichier introuvable : {source}")

    print(f"\nAjout du tableau à partir de : {source.name}\n")
    titre = demander("Titre de l'œuvre")
    technique = demander("Technique", "Huile sur toile")
    dimensions = demander("Dimensions (ex: 60 × 73 cm)", "")
    annee = demander("Année", str(__import__("datetime").date.today().year))

    DOSSIER_IMAGES.mkdir(exist_ok=True)
    nom = source.name.lower().replace(" ", "-")
    if not nom.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        nom += ".jpg"
    cible = DOSSIER_IMAGES / nom
    i = 1
    while cible.exists():
        cible = DOSSIER_IMAGES / f"{Path(nom).stem}-{i}{Path(nom).suffix}"
        i += 1

    shutil.copy2(source, cible)
    empreinte = proteger_image(cible)
    if cible.suffix.lower() == ".png":
        png = cible
        cible = png.with_suffix(".jpg")
        png.rename(cible)
        empreinte = proteger_image(cible)

    galerie = json.loads(GALERIE.read_text(encoding="utf-8"))
    galerie["oeuvres"].append({
        "titre": titre,
        "technique": technique,
        "dimensions": dimensions,
        "annee": annee,
        "artiste": ARTISTE,
        "image": f"images/{cible.name}",
    })
    GALERIE.write_text(json.dumps(galerie, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\nŒuvre « {titre} » ajoutée : images/{cible.name}")
    print(f"Filigrane © Dreymlz appliqué. Empreinte sha256 : {empreinte}")
    print("Envoyez les fichiers modifiés (galerie.json + images/) pour publier.")


if __name__ == "__main__":
    main()
