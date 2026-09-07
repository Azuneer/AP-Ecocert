# Mission 1 : Plan d'adressage VLSM

![Logo Ecocert](../assets/ecocertlogo.jpg){ width="150" }

> :bust_in_silhouette: **Fiche rédigée par** : GADONNAUD Ewen & Rayan BOINA BOINA  
> :mortar_board: **Formation** : BTS SIO 2ème année - Option SISR  
> :school: **Établissement** : Lycée Paul-Louis Courier, Tours  
> :calendar: **Date** : Septembre 2026

---

## Objectif

Segmenter le réseau `192.168.3.0/24` (groupe VLAN 53) en utilisant la méthode **VLSM** (Variable Length Subnet Masking) selon les besoins de chaque service, avec une marge de **20%** d'adresses supplémentaires par sous-réseau.

Le réseau **serveurs** (`172.16.53.0/24`) reste, lui, à l'identique.

## Calcul des besoins

Pour chaque service : `besoin = nombre d'hôtes × 1,2`, arrondi à la puissance de 2 supérieure (moins 2 adresses pour le réseau et le broadcast).

| VLAN | Service(s) | Hôtes | +20% | Besoin réel | Bits hôtes | Sous-réseau | Masque |
|------|------------|------:|-----:|------------:|-----------:|-------------|--------|
| **11** | Administration | 45 | 54 | 62 | 6 | `/26` | 255.255.255.192 |
| **21** | Certification | 20 | 24 | 30 | 5 | `/27` | 255.255.255.224 |
| **81** | Wifi-Visiteurs | 20 | 24 | 30 | 5 | `/27` | 255.255.255.224 |
| **61** | Expertise technique / conseil | 15 | 18 | 30 | 5 | `/27` | 255.255.255.224 |
| **31** | Référentiels | 12 | 15 | 30 | 5 | `/27` | 255.255.255.224 |
| **71** | Services techniques | 10 | 12 | 14 | 4 | `/28` | 255.255.255.240 |
| **41** | Formations professionnelles | 8 | 10 | 14 | 4 | `/28` | 255.255.255.240 |

!!! note "Vérification"
    **64 + 32 + 32 + 32 + 32 + 16 + 16 = 224** adresses consommées sur les 256 du `/24`, soit une réserve de **32 adresses** pour une extension future.

## Plan d'adressage VLSM

Allocation dans l'ordre décroissant des besoins (du plus grand masque au plus petit) :

| VLAN | Service | Adresse réseau | Masque | Plage d'hôtes utilisables | Passerelle | Broadcast |
|------|---------|----------------|--------|---------------------------|-----------|-----------|
| **11** | Administration | 192.168.3.0/26 | 255.255.255.192 | 192.168.3.1 – 192.168.3.62 | 192.168.3.62 | 192.168.3.63 |
| **21** | Certification | 192.168.3.64/27 | 255.255.255.224 | 192.168.3.65 – 192.168.3.94 | 192.168.3.94 | 192.168.3.95 |
| **81** | Wifi-Visiteurs | 192.168.3.96/27 | 255.255.255.224 | 192.168.3.97 – 192.168.3.126 | 192.168.3.126 | 192.168.3.127 |
| **61** | Expertise / conseil | 192.168.3.128/27 | 255.255.255.224 | 192.168.3.129 – 192.168.3.158 | 192.168.3.158 | 192.168.3.159 |
| **31** | Référentiels | 192.168.3.160/27 | 255.255.255.224 | 192.168.3.161 – 192.168.3.190 | 192.168.3.190 | 192.168.3.191 |
| **71** | Services techniques | 192.168.3.192/28 | 255.255.255.240 | 192.168.3.193 – 192.168.3.206 | 192.168.3.206 | 192.168.3.207 |
| **41** | Formations | 192.168.3.208/28 | 255.255.255.240 | 192.168.3.209 – 192.168.3.222 | 192.168.3.222 | 192.168.3.223 |

> **Convention retenue** : la passerelle est placée sur la **dernière** adresse utilisable de chaque sous-réseau (`.62`, `.94`, `.126`, `.158`, `.190`, `.206`, `.222`).

### Plage restante (réserve)

`192.168.3.224` à `192.168.3.255` (soit **32 adresses**) — réserve pour une évolution future (nouveau service, extension d'un VLAN existant).

## Réseau serveurs

Le réseau serveurs `172.16.53.0/24` n'est pas segmenté. Les adresses des serveurs sont les suivantes :

| Serveur | IP | Service |
|---------|-----|---------|
| ADECOCERT | 172.16.53.1 | AD + DNS |
| DHCPECOCERT | 172.16.53.2 | DHCP |
| NASECOCERT | 172.16.53.20 | Sauvegardes |
| WIFIECOCERT | 172.16.53.30 | Contrôleur WiFi |
| GLPIECOCERT | 172.16.53.40 | Gestion d'incidents |

!!! info "Remarque"
    « 5X » avec X = numéro du groupe. Pour le groupe du VLAN 53, X = 3, d'où `172.16.53.0/24`. Ce réseau n'est **pas** en adressage dynamique (exclu du DHCP).

## Validation

Le plan d'adressage a bien été validé par l'équipe d'enseignants.

## Documentation complémentaire

- [VLSM](../documentation/reseau/vlsm.md)
- [VLAN](../documentation/reseau/vlan.md)
