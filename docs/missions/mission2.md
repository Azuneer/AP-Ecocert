# Mission 2 : AD + DHCP

![Logo Ecocert](../assets/ecocertlogo.jpg){ width="150" }

> :bust_in_silhouette: **Fiche rédigée par** : GADONNAUD Ewen & Rayan BOINA BOINA  
> :mortar_board: **Formation** : BTS SIO 2ème année - Option SISR  
> :school: **Établissement** : Lycée Paul-Louis Courier, Tours  
> :calendar: **Date** : Septembre 2026

---

## Objectif

Déployer deux serveurs dans un environnement virtuel (Proxmox) :

1. Un **contrôleur de domaine** Windows 2019 avec DNS dynamique et Active Directory
2. Un **serveur DHCP** Debian distribuant les paramètres réseau à tous les sous-réseaux

## Serveur 1 — ADECOCERT (AD + DNS)

| Paramètre | Valeur |
|-----------|--------|
| Nom | ADECOCERT |
| IP | 172.16.5X.1 |
| OS | Windows 2019 Server |
| Domaine | local.ecocertX.fr |
| Services | DNS dynamique, Active Directory |

- Peupler l'AD avec le script PowerShell et le fichier CSV mis à disposition
- Compléter les commentaires du script pour expliquer les structures de programmation

## Serveur 2 — DHCPECOCERT

| Paramètre | Valeur |
|-----------|--------|
| Nom | DHCPECOCERT |
| IP | 172.16.5X.2 |
| OS | Debian |
| Service | DHCP |

!!! warning "Contrainte"
    Tous les sous-réseaux doivent être en adressage dynamique **sauf** le réseau serveurs.

Le service DHCP doit distribuer l'ensemble des paramétrages réseau pour tous les sous-réseaux de la société.

## Documentation complémentaire

- [Windows Server](../documentation/adminsys/windows-server.md)
- [Debian](../documentation/adminsys/debian.md)
- [DHCP](../documentation/services/dhcp.md)