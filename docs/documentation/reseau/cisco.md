# Cisco

Documentation relative à la configuration des équipements **Cisco** utilisés dans le projet Ecocert.

## Équipements

| Modèle | Niveau | Rôle |
|--------|--------|------|
| Cisco 9200 | Niveau 3 | Cœur de réseau — routage inter-VLAN |
| Cisco 2960 | Niveau 2 | Commutateur d'accès — segmentation VLAN |

## Commandes de base

```cisco
! Mode privileged
enable
configure terminal

! Configuration VLAN
vlan <id>
name <nom>

! Attribution de port à un VLAN
interface <port>
switchport mode access
switchport access vlan <id>

! Trunk (liaison inter-VLAN)
interface <port>
switchport mode trunk
switchport trunk allowed vlan <liste>

! Routage inter-VLAN (L3)
ip routing
interface vlan <id>
ip address <ip> <masque>
no shutdown
```

## Voir aussi

- [VLAN](vlan.md)
- [VLSM](vlsm.md)