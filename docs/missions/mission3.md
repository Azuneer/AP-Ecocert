# Mission 3 : GLPI + NAS

![Logo Ecocert](../assets/ecocertlogo.jpg){ width="150" }

> :bust_in_silhouette: **Fiche rédigée par** : GADONNAUD Ewen & Rayan BOINA BOINA  
> :mortar_board: **Formation** : BTS SIO 2ème année - Option SISR  
> :school: **Établissement** : Lycée Paul-Louis Courier, Tours  
> :calendar: **Date** : Septembre 2026

---

## Objectif

Déployer un serveur de gestion d'incidents et un serveur NAS de sauvegarde.

## Serveur 1 — GLPIECOCERT

| Paramètre | Valeur |
|-----------|--------|
| Nom | GLPIECOCERT |
| IP | 172.16.5X.40 |
| OS | À déterminer (en argumentant) |
| Service | GLPI — Gestion d'inventaire et de tickets d'incident |

!!! info "Responsables tickets"
    - **Olivier TONDET** : solutions techniques d'accès et éléments d'interconnexion
    - **Pamela TREMO** : services et systèmes serveurs

L'inventaire est réalisé en grande partie par une remontée automatique des composants des postes de travail.

## Serveur 2 — NASECOCERT

| Paramètre | Valeur |
|-----------|--------|
| Nom | NASECOCERT |
| IP | 172.16.5X.20 |
| OS | À déterminer |
| Service | Sauvegardes |

!!! warning "Configuration RAID"
    - **RAID 5** avec au minimum **20 Go** disponibles pour les données
    - Accès via authentification par **Active Directory**

## Documentation complémentaire

- [GLPI](../documentation/services/glpi.md)
- [NAS](../documentation/services/nas.md)