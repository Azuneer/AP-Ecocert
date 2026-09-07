# AP-Ecocert

Atelier de professionnalisation de 2ème année de BTS SIO (option SISR) dans le contexte Ecocert.

## Présentation

Ce projet porte sur la modernisation de l'infrastructure réseau de la société Ecocert, organisme de certification de pratiques durables. Il se décline en quatre missions : plan d'adressage VLSM, déploiement d'un contrôleur de domaine et d'un serveur DHCP, mise en place de serveurs GLPI et NAS, et configuration de l'architecture réseau (Cisco, Stormshield, WiFi Ubiquiti).

La documentation complète est générée avec **MkDocs** et publiée automatiquement sur **GitHub Pages** via GitHub Actions.

## Auteurs

- Ewen GADONNAUD
- Rayan BOINA BOINA

## Missions

1. Plan d'adressage VLSM
2. Contrôleur de domaine (AD) + DHCP
3. GLPI + NAS
4. Architecture réseau

## Développement local

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve
```

Rendez-vous sur <http://127.0.0.1:8000> pour prévisualiser le site.

## Déploiement

À chaque push sur `main`, l'action GitHub déploie automatiquement le site sur GitHub Pages.
