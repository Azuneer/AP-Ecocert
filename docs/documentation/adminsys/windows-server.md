# Windows Server

Documentation relative à l'administration de **Windows Server 2019** dans le contexte Ecocert.

## Services déployés

- **Active Directory** : annuaire centralisé du domaine `local.ecocertX.fr`
- **DNS dynamique** : résolution de noms associée à l'AD

## Serveur ADECOCERT

| Paramètre | Valeur |
|-----------|--------|
| Nom | ADECOCERT |
| IP | 172.16.5X.1 |
| Domaine | local.ecocertX.fr |
| Rôle | Contrôleur de domaine |

## Peuplement de l'AD

Le script PowerShell et le fichier CSV fournis permettent de créer automatiquement les utilisateurs et structures organisationnelles.

!!! info "Script"
    Compléter les commentaires manquants du script pour expliquer les structures de programmation mobilisées et leurs objectifs.

## Voir aussi

- [Debian](debian.md)
- [DHCP](../services/dhcp.md)