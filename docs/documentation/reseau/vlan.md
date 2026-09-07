# VLAN

Un **VLAN** (Virtual Local Area Network) permet de segmenter logiquement un réseau physique en plusieurs réseaux virtuels, isolant le trafic entre groupes de machines même si elles sont connectées au même commutateur.

## Intérêts

- **Sécurité** : isolation des flux entre services
- **Performance** : réduction du domaine de diffusion (broadcast)
- **Organisation** : regroupement logique par service ou fonction

## Configuration sur Cisco

```cisco
Switch(config)# vlan 11
Switch(config-vlan)# name Administration
Switch(config)# interface range fa0/1-10
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 11
```

## Routage inter-VLAN

Le routage inter-VLAN s'effectue via un **commutateur de niveau 3** (Cisco 9200) ou un pare-feu. Chaque VLAN correspond à un sous-réseau distinct.

## Voir aussi

- [VLSM](vlsm.md)
- [Cisco](cisco.md)