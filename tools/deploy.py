#!/usr/bin/env python3
"""Déploie le site sur l'hébergement (FTP ou SFTP), sans identifiants en dur.

Configuration : créer deploy.local.json à la racine (jamais versionné) :

    {
      "protocol": "ftp",                  // "ftp" ou "sftp"
      "host": "ftp.mon-hebergement.fr",
      "port": 21,                         // 21 (ftp) ou 22 (sftp)
      "user": "mon-login",
      "password": "mon-mot-de-passe",
      "remote_dir": "/www/galerie"        // dossier racine du site chez l'hébergeur
    }

Usage :
    python3 tools/deploy.py            // envoie tous les fichiers web
    python3 tools/deploy.py --dry-run  // liste ce qui serait envoyé
"""
import ftplib
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONFIG = RACINE / "deploy.local.json"

FICHIERS_WEB = ["index.html", "styles.css", "script.js", "galerie.json"]
DOSSIERS_WEB = ["images"]


def fichiers_a_envoyer() -> list[Path]:
    fichiers = [RACINE / f for f in FICHIERS_WEB if (RACINE / f).exists()]
    for dossier in DOSSIERS_WEB:
        d = RACINE / dossier
        if d.exists():
            fichiers += sorted(p for p in d.rglob("*") if p.is_file())
    return fichiers


def relatif(p: Path) -> str:
    return p.relative_to(RACINE).as_posix()


def deploy_ftp(cfg: dict, fichiers: list[Path], dry: bool) -> None:
    if dry:
        for f in fichiers:
            print(f"[dry-run] ftp://{cfg['host']}{cfg['remote_dir']}/{relatif(f)}")
        return
    with ftplib.FTP() as ftp:
        ftp.connect(cfg["host"], cfg.get("port", 21), timeout=30)
        ftp.login(cfg["user"], cfg["password"])
        ftp.cwd(cfg["remote_dir"])
        for f in fichiers:
            dest = relatif(f)
            dossiers = dest.split("/")[:-1]
            for d in dossiers:
                try:
                    ftp.mkd(d)
                except ftplib.error_perm:
                    pass
                ftp.cwd(d)
            with open(f, "rb") as fh:
                ftp.storbinary(f"STOR {dest.split('/')[-1]}", fh)
            for _ in dossiers:
                ftp.cwd("..")
            print(f"envoyé : {dest}")


def deploy_sftp(cfg: dict, fichiers: list[Path], dry: bool) -> None:
    try:
        import paramiko
    except ImportError:
        sys.exit("SFTP requiert paramiko : pip install paramiko")
    if dry:
        for f in fichiers:
            print(f"[dry-run] sftp://{cfg['host']}{cfg['remote_dir']}/{relatif(f)}")
        return
    transport = paramiko.Transport((cfg["host"], cfg.get("port", 22)))
    transport.connect(username=cfg["user"], password=cfg["password"])
    sftp = paramiko.SFTPClient.from_transport(transport)
    for f in fichiers:
        dest = f"{cfg['remote_dir'].rstrip('/')}/{relatif(f)}"
        dossiers = dest.split("/")[1:-1]
        courant = ""
        for d in dossiers:
            courant += f"/{d}"
            try:
                sftp.mkdir(courant)
            except IOError:
                pass
        sftp.put(str(f), dest)
        print(f"envoyé : {relatif(f)}")
    transport.close()


def main() -> None:
    dry = "--dry-run" in sys.argv
    if not CONFIG.exists():
        sys.exit(
            "Créez deploy.local.json à la racine du projet (voir README, section "
            "Déploiement). Ce fichier est ignoré par git : vos identifiants ne "
            "seront jamais publiés."
        )
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    fichiers = fichiers_a_envoyer()
    print(f"{len(fichiers)} fichier(s) à déployer vers {cfg['host']}{cfg['remote_dir']}")
    if cfg.get("protocol", "ftp") == "sftp":
        deploy_sftp(cfg, fichiers, dry)
    else:
        deploy_ftp(cfg, fichiers, dry)
    if not dry:
        print("Déploiement terminé.")


if __name__ == "__main__":
    main()
