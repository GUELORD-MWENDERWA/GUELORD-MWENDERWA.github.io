# Maquettes

Le site est sa propre maquette : chaque page est capturée à 390 px (téléphone) et 1440 px (bureau), en clair et en sombre, par `tools/apercu.mjs`. L'outil fait défiler la page pour charger les images différées et sort en erreur sur un débordement horizontal, une image cassée, une erreur JS ou une requête en échec.

| Capture | Page |
| --- | --- |
| `captures/390/accueil.jpg`, `captures/1440/accueil.jpg` | Accueil anglais (`/`) |
| `captures/*/accueil-sombre.jpg` | Accueil anglais, thème sombre |
| `captures/*/fr.jpg`, `captures/*/fr-sombre.jpg` | Accueil français (`/fr/`) |
| `captures/*/404.jpg` | Page 404 bilingue |

Dernier contrôle : 0 débordement, 0 erreur sur les 10 captures.
