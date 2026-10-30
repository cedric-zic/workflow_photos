# Galerie DreyM

Site statique de présentation des tableaux de **DreyM**, rendu façon galerie
d'art : chaque toile est présentée dans un **cadre doré/bois** avec un
**cartel** (titre, technique, dimensions, année), sur un mur sombre. Clic sur
une œuvre pour l'afficher en grand avec navigation clavier (← →, Échap).

Aucune build, aucun framework : HTML / CSS / JS purs + un fichier `galerie.json`.

## Structure

| Fichier | Rôle |
|---|---|
| `index.html` | Page unique de la galerie |
| `styles.css` | Mur, cadres, cartels, visionneuse plein écran |
| `script.js` | Charge `galerie.json`, construit le mur et la visionneuse |
| `galerie.json` | **Liste des œuvres** — c'est le seul fichier à éditer pour gérer le contenu |
| `images/` | Photos des toiles (filigranées) |
| `tools/watermark.py` | Applique le filigrane + métadonnées sur une image |
| `tools/add_tableau.py` | Ajoute une œuvre (voir ci-dessous) |
| `tools/remove_tableau.py` | Supprime une œuvre (voir ci-dessous) |

## Ajouter un tableau (sans code)

```bash
python3 tools/add_tableau.py chemin/vers/ma-photo.jpg
```

Le script pose quelques questions (titre, technique, dimensions, année), copie
la photo dans `images/`, applique le **filigrane © Dreymlz** et les métadonnées
de copyright, puis ajoute l'œuvre à `galerie.json`.

Alternative manuelle : déposer l'image dans `images/` et ajouter un bloc dans
`galerie.json` :

```json
{
  "titre": "Mon nouveau tableau",
  "technique": "Huile sur toile",
  "dimensions": "60 × 73 cm",
  "annee": "2026",
  "image": "images/mon-tableau.jpg"
}
```

## Supprimer un tableau (sans code)

```bash
python3 tools/remove_tableau.py
```

Choisir le numéro de l'œuvre : elle est retirée de `galerie.json` et son image
est supprimée de `images/`.

## Protection des œuvres (anti-vol)

Chaque image publiée porte :

- un **filigrane « © Dreymlz »** en tuile diagonale très transparente
  (lisible sur un fichier téléchargé, quasi invisible à l'écran) ;
- une **signature en coin inférieur droit** ;
- des **métadonnées EXIF** : `Artist = DreyM`, `Copyright = © Dreymlz — Tous droits réservés`,
  plus l'empreinte SHA-256 affichée à l'ajout (preuve d'antériorité) ;
- côté site : clic droit désactivé sur les images et pied de page de copyright.

> Ces mesures dissuadent le vol occasionnel et prouvent la paternité. Elles ne
> remplacent pas un dépôt légal (INPI, e-Soleau) pour les œuvres à fort enjeu.

Pour re-filigraner une image existante :

```bash
python3 tools/watermark.py images/mon-image.jpg
```

## Déploiement

Le site fonctionne en ouvrant `index.html` directement, ou via n'importe quel
hébergement statique (GitHub Pages : dépôt public → Settings → Pages →
Deploy from branch `main`, dossier `/`). Le chargement de `galerie.json` en
`fetch` nécessite de servir le site par HTTP (GitHub Pages convient) plutôt
qu'un simple double-clic sur le fichier.

### Déployer sur son propre hébergement (OVH ou autre)

1. Créer `deploy.local.json` à la racine du projet (ignoré par git, donc
   jamais publié) :

   ```json
   {
     "protocol": "ftp",
     "host": "ftp.mon-hebergement.fr",
     "port": 21,
     "user": "mon-login",
     "password": "mon-mot-de-passe",
     "remote_dir": "/www/galerie"
   }
   ```

   Pour du SFTP : `"protocol": "sftp"`, `"port": 22` (nécessite `pip install paramiko`).

2. Déployer :

   ```bash
   python3 tools/deploy.py --dry-run   # vérifie la liste des fichiers
   python3 tools/deploy.py             # envoie index.html, styles.css, script.js,
                                       # galerie.json et images/ sur le serveur
   ```

### Redirection OVH (nom de domaine → hébergement)

Dans l'espace client OVH → **Noms de domaine → Zone DNS** :

- Si le site est à la racine de l'hébergement : enregistrement `A` (ou `AAAA`)
  sur le domaine racine pointant vers l'IP de l'hébergement, plus `CNAME` sur
  `www` vers le domaine racine.
- Si le site est dans un sous-dossier (`/galerie/`) : `CNAME` de `www` (et
  redirection 301 du domaine racine) vers l'URL cible, ou redirection via
  **Multisite / Redirection** du manager OVH.
- Pour un sous-domaine dédié (recommandé, ex. `galerie.mondomaine.fr`) :
  enregistrement `A` de `galerie` vers l'IP de l'hébergement, puis le dossier
  `www/galerie` de l'hébergement sert le site sur ce sous-domaine.

> Ne jamais mettre d'identifiants FTP dans un fichier versionné :
> `deploy.local.json` est dans `.gitignore`.

Dépendance des outils Python : `pip install pillow` (+ `paramiko` pour SFTP).
