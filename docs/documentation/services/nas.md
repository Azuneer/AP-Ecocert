# NAS

Un **NAS** (Network Attached Storage) est un serveur de stockage en réseau dédié à la sauvegarde et au partage de fichiers.

## Serveur NASECOCERT

| Paramètre | Valeur |
|-----------|--------|
| Nom | NASECOCERT |
| IP | 172.16.5X.20 |
| OS | À déterminer |
| Service | Sauvegardes |

## Configuration RAID 5

Le **RAID 5** distribue les données et les parités sur au moins 3 disques, offrant un bon compromis entre performance, capacité et tolérance de panne.

!!! warning "Exigence"
    - Minimum **20 Go** disponibles pour les données
    - Accès via authentification par **Active Directory**

| Disques requis | Tolérance | Espace utile |
|----------------|-----------|--------------|
| ≥ 3 | 1 disque | (n-1) × taille disque |

## Voir aussi

- [GLPI](glpi.md)
- [Debian](../adminsys/debian.md)