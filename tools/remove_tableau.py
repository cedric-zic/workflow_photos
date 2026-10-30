#!/usr/bin/env python3
"""Supprime un tableau de la galerie, sans toucher au code.

Usage :
    python3 tools/remove_tableau.py

Liste les œuvres avec leur numéro, demande lequel supprimer,
retire l'entrée de galerie.json et supprime le fichier image.
"""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
GALERIE = RACINE / "galerie.json"


def main() -> None:
    galerie = json.loads(GALERIE.read_text(encoding="utf-8"))
    oeuvres = galerie["oeuvres"]
    if not oeuvres:
        print("La galerie est déjà vide.")
        return

    print("Œuvres actuellement dans la galerie :\n")
    for i, o in enumerate(oeuvres, 1):
        print(f"  {i}. {o['titre']} ({o.get('annee', '?')}) — {o['image']}")

    saisie = input("\nNuméro de l'œuvre à supprimer (ou 'annuler') : ").strip().lower()
    if saisie in ("", "annuler", "a"):
        print("Suppression annulée.")
        return
    try:
        index = int(saisie) - 1
        oeuvre = oeuvres[index]
    except (ValueError, IndexError):
        sys.exit("Numéro invalide.")

    image = RACINE / oeuvre["image"]
    if image.exists():
        image.unlink()

    del oeuvres[index]
    GALERIE.write_text(json.dumps(galerie, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"« {oeuvre['titre']} » supprimée de la galerie (image supprimée aussi).")


if __name__ == "__main__":
    main()
