# Portfolio — consignes

Site statique servi par GitHub Pages depuis `main` (racine). Push sur `main` = mise en ligne en une minute.

- Le texte vit dans `content/en.toml` et `content/fr.toml` : toujours modifier les deux langues, puis `python3 tools/build.py` et `python3 tools/check.py` (0 problème). Ne jamais éditer `index.html` ou `fr/index.html` à la main.
- Couleurs, tailles de texte et rayons : seulement les jetons de `assets/site.css` (`:root`). `tools/check.py` refuse le reste.
- Maquette d'abord : toute nouvelle section se vérifie avec `tools/apercu.mjs` à 390 et 1440 px, clair et sombre, avant le push.
- **Mwangaza se présente par son site (mwangazaschool.com), jamais par son dépôt GitHub** : pas de lien vers `GUELORD-MWENDERWA/mwangaza`, pas de nombre de commits ou de PR (le contrôle le vérifie).
- Contributions open source : ajouter une entrée `[[pr]]` dans `content/contributions.toml` (repo, title, url, state = open / merged / closed) et mettre l'état à jour quand la PR est fusionnée.
- **Seulement l'utile** pour qui veut contacter Guelord ou voir son travail (demande du 2026-10-20) : pas de mention technique du site, de lien vers son code, de crédits ni de détails d'infrastructure (taille du serveur, hébergeur, logiciel serveur). Pied de page = « © année Guelord Mwenderwa ».
- Images : nos propres captures et figures seulement (une photo sous licence imposerait un crédit visible) ; sources passées par `tools/images.py` (WebP en deux largeurs), listées dans `assets/img/ATTRIBUTIONS.md`.
