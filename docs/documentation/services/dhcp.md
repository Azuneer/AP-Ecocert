# DHCP

Le **DHCP** (Dynamic Host Configuration Protocol) distribue automatiquement les paramètres réseau (adresse IP, masque, passerelle, DNS) aux machines d'un réseau.

## Serveur DHCPECOCERT

| Paramètre | Valeur |
|-----------|--------|
| Nom | DHCPECOCERT |
| IP | 172.16.5X.2 |
| OS | Debian |
| Portée | Tous les sous-réseaux sauf le réseau serveurs |

## Principe de fonctionnement

1. **DISCOVER** : le client diffuse une demande
2. **OFFER** : le serveur propose une adresse
3. **REQUEST** : le client accepte l'adresse
4. **ACK** : le serveur confirme l'attribution

## Contraintes

!!! warning "Réseau serveurs exclu"
    Le réseau serveurs (`5X`) ne doit **pas** être en adressage dynamique. Seuls les postes clients reçoivent une IP via DHCP.

Le service DHCP doit distribuer les paramètres pour **tous** les sous-réseaux de la société.

## Voir aussi

- [NAS](nas.md)
- [Debian](../adminsys/debian.md)