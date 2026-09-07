# AP-ECOCERT

![Logo Ecocert](./assets/ecocertlogo.jpg){ width="250" }

Atelier de Professionnalisation — BTS SIO 2ème année, Option SISR.

---

## Contexte

Le projet porte sur la société **ECOCERT**, organisme de certification de pratiques durables (agriculture biologique, écoproduits, développement durable). Ecocert souhaite moderniser son infrastructure réseau pour accompagner sa croissance.

Actuellement, plusieurs problèmes sont constatés :

- Ralentissements du trafic réseau
- Nécessité de segmenter le réseau en sous-réseaux (VLSM)
- Installation d'une ferme de serveurs Proxmox nécessitant un adressage dédié
- Besoin de services centralisés (AD, DHCP, GLPI, NAS)

## Missions

<div class="grid cards" markdown>

- :material-map-marker-distance:{ .lg .middle } __Mission 1 : Plan d'adressage__

    ---

    Segmenter le réseau `192.168.X.0/24` en VLSM selon les besoins de chaque service.

    [:octicons-arrow-right-24: Découvrir](missions/mission1.md)

- :material-server:{ .lg .middle } __Mission 2 : AD + DHCP__

    ---

    Déployer un contrôleur de domaine Windows 2019 et un serveur DHCP Debian.

    [:octicons-arrow-right-24: Découvrir](missions/mission2.md)

- :material-clipboard-check-outline:{ .lg .middle } __Mission 3 : GLPI + NAS__

    ---

    Mettre en place un serveur GLPI et un serveur NAS en RAID 5.

    [:octicons-arrow-right-24: Découvrir](missions/mission3.md)

- :material-router-network:{ .lg .middle } __Mission 4 : Architecture réseau__

    ---

    Configurer switches Cisco, pare-feu Stormshield et borne WiFi Ubiquiti.

    [:octicons-arrow-right-24: Découvrir](missions/mission4.md)

</div>

## Équipe

- **Auteurs** : Ewen GADONNAUD & Rayan BOINA BOINA
- **Formation** : BTS SIO 2ème année — Option SISR, Lycée Paul-Louis Courier, Tours
- **Date de livraison** : 28/09/2026

## Déploiement

Ce site est propulsé par [MkDocs Material](https://squidfunnel.github.io/mkdocs-material/) et déployé automatiquement via **GitHub Actions** sur **GitHub Pages**. À chaque push sur `main`, le site est compilé, testé et publié sans intervention manuelle.