/* Galerie DreyM — chargement des œuvres depuis galerie.json */

const ARTISTE = "DreyM";

let oeuvres = [];
let indexCourant = 0;

const mur = document.getElementById("mur");
const chargement = document.getElementById("chargement");
const visionneuse = document.getElementById("visionneuse");
const vImg = document.getElementById("visionneuse-img");
const vCartel = document.getElementById("visionneuse-cartel");

document.getElementById("annee").textContent = new Date().getFullYear();

function cartelHTML(o) {
  const details = [o.technique, o.dimensions, o.annee].filter(Boolean).join(" — ");
  return `
    <div class="titre">${o.titre}</div>
    ${details ? `<div class="details">${details}</div>` : ""}
    <div class="artiste">${o.artiste || ARTISTE}</div>`;
}

function afficherMur() {
  mur.innerHTML = "";
  oeuvres.forEach((o, i) => {
    const figure = document.createElement("figure");
    figure.className = "oeuvre";
    figure.innerHTML = `
      <div class="cadre">
        <img src="${o.image}" alt="${o.titre} — peinture de ${o.artiste || ARTISTE}" loading="lazy"
             oncontextmenu="return false">
      </div>
      <figcaption class="cartel">${cartelHTML(o)}</figcaption>`;
    figure.addEventListener("click", () => ouvrir(i));
    mur.appendChild(figure);
  });
  chargement.remove();
}

function ouvrir(i) {
  indexCourant = i;
  const o = oeuvres[i];
  vImg.src = o.image;
  vImg.alt = `${o.titre} — peinture de ${o.artiste || ARTISTE}`;
  vCartel.innerHTML = cartelHTML(o);
  visionneuse.hidden = false;
  document.body.style.overflow = "hidden";
}

function fermer() {
  visionneuse.hidden = true;
  document.body.style.overflow = "";
}

function naviguer(delta) {
  indexCourant = (indexCourant + delta + oeuvres.length) % oeuvres.length;
  ouvrir(indexCourant);
}

document.getElementById("fermer").addEventListener("click", fermer);
document.getElementById("prec").addEventListener("click", () => naviguer(-1));
document.getElementById("suiv").addEventListener("click", () => naviguer(1));
visionneuse.addEventListener("click", (e) => { if (e.target === visionneuse) fermer(); });
document.addEventListener("keydown", (e) => {
  if (visionneuse.hidden) return;
  if (e.key === "Escape") fermer();
  if (e.key === "ArrowLeft") naviguer(-1);
  if (e.key === "ArrowRight") naviguer(1);
});

fetch("galerie.json")
  .then((r) => {
    if (!r.ok) throw new Error("galerie.json introuvable");
    return r.json();
  })
  .then((data) => {
    oeuvres = data.oeuvres;
    afficherMur();
  })
  .catch((err) => {
    chargement.textContent = "Impossible de charger la galerie : " + err.message;
  });
