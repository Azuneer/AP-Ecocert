# VLSM

**VLSM** (Variable Length Subnet Masking) est une technique de découpage de réseau permettant d'attribuer des masques de sous-réseaux de taille variable à différents sous-réseaux, optimisant ainsi l'utilisation des adresses IP.

## Principe

Contrairement au **FLSM** (Fixed Length Subnet Masking) qui utilise un masque unique pour tous les sous-réseaux, le VLSM adapte la taille de chaque sous-réseau au nombre réel d'hôtes nécessaires.

## Méthode de calcul

1. **Lister** les besoins en hôtes par sous-réseau (du plus grand au plus petit)
2. **Ajouter la marge** demandée (20% dans le contexte Ecocert) : `besoin = hôtes × 1,2`
3. **Calculer** la taille requise : `2^n - 2 ≥ besoin réel`
4. **Attribuer** les plages d'adresses consécutives
5. **Vérifier** qu'il n'y a pas de chevauchement

!!! example "Exemple"
    Pour un service de 45 hôtes + 20% = 54 hôtes nécessaires :
    - `2^6 - 2 = 62 ≥ 54` → masque `/26`
    - Plage : `192.168.1.0/26` → `192.168.1.1` à `192.168.1.62`

## Formules utiles

| Formule | Description |
|---------|-------------|
| `2^n - 2 ≥ hôtes` | Nombre d'adresses utilisables avec n bits hôte |
| `2^n ≥ hôtes × 1,2` | Taille avec marge de 20% |
| Masque CIDR = `32 - n` | Masque de sous-réseau en notation CIDR |
| Dernière adresse = réseau + 2^n - 1 | Adresse de broadcast |

## Voir aussi

- [VLAN](vlan.md)
- [Plan d'adressage (Mission 1)](../../missions/mission1.md)