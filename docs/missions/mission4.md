# Mission 4 : Architecture réseau

![Logo Ecocert](../assets/ecocertlogo.jpg){ width="150" }

> :bust_in_silhouette: **Fiche rédigée par** : GADONNAUD Ewen & Rayan BOINA BOINA  
> :mortar_board: **Formation** : BTS SIO 2ème année - Option SISR  
> :school: **Établissement** : Lycée Paul-Louis Courier, Tours  
> :calendar: **Date** : Septembre 2026

---

## Objectif

Configurer l'architecture réseau complète : commutateurs, pare-feu et borne WiFi.

## Équipements

| Équipement | Rôle |
|------------|------|
| Cisco 9200 | Commutateur de cœur — routage inter-VLAN |
| Cisco 2960 | Commutateur d'accès |
| Stormshield SN210 (VM « EVA ») | Pare-feu UTM — NAT/PAT et filtrage |
| Ubiquiti Unifi U6+ | Borne WiFi — 2 SSID |

## Répartition des tâches

### Commutateurs

- **Cisco 2960** (accès) : segmentation VLAN selon le plan d'adressage
- **Cisco 9200** (cœur) : routage inter-VLAN

### Pare-feu Stormshield « EVA »

- VM Stormshield SN210
- Règle de **NAT dynamique (NAPT)** pour la sortir sur Internet
- Traduction NAPT de toutes les adresses privées vers l'adresse du réseau WAN-SIO
- Politique 10 avec règle de masquerading

!!! warning "Règle NAT"
    Définir explicitement l'interface de sortie (`out`) dans la destination originale pour éviter le blocage des flux d'administration (SSH/HTTPS).

### Borne WiFi Ubiquiti Unifi U6+

| SSID | VLAN | Sécurité |
|------|------|----------|
| Wifi-Visiteurs | 81 | WPA2/WPA3 — `SIO-sisr2-ap2026` |
| Service-Technique | 71 | WPA2/WPA3 — `SIO-sisr2-ap2026` |

!!! info "Contrôleur WiFi"
    Le contrôleur **Unifi OS** doit être installé sur un serveur Linux Debian ou Windows Server.

#### Serveur contrôleur WiFi

| Paramètre | Valeur |
|-----------|--------|
| Nom | WIFIECOCERT |
| IP | 172.16.5X.30 |
| OS | À déterminer |
| Service | Gestion des bornes WiFi |

## Contraintes matérielles et technologiques

- Ferme de serveurs **Proxmox**
- Licence **Windows 2019 Server** dédiée AD/DNS
- **Debian** pour les services utilisateurs (DHCP, NAS…)
- Cisco 9200 (cœur) + Cisco 2960 (accès)
- Stormshield SN210 virtuel
- Borne Ubiquiti Unifi U6+
- Traduction **NAPT** sur le pare-feu vers le réseau WAN-SIO

## Maquette

Préparer sous **Packet Tracer** la maquette de l'implantation, la tester et la mettre en place.

Tests requis :

- Vérification du respect des règles de routage
- Distribution des adresses IP en DHCP pour tous les services

## Documentation complémentaire

- [Stormshield](../documentation/cybersecurite/stormshield.md)
- [Cisco](../documentation/reseau/cisco.md)
- [VLAN](../documentation/reseau/vlan.md)