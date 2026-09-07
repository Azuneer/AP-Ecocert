# Stormshield

Documentation relative au pare-feu **UTM Stormshield SN210** (VM « EVA ») utilisé dans le projet Ecocert.

## Rôle dans l'architecture

Le pare-feu Stormshield assure la sécurité du réseau et la traduction d'adresses (NAT/PAT) pour la connexion Internet.

## NAT dynamique (NAPT)

Le NAT dynamique permet aux machines du réseau interne d'accéder à Internet en traduisant les adresses privées vers une adresse publique.

### Principe du PAT

Le **PAT** (Port Address Translation) est un type de NAT dynamique qui utilise le numéro de port pour multiplexer plusieurs connexions sur une seule adresse IP. Le nombre maximal de traductions est de **65 536** (ports codés sur 16 bits).

### Configuration sur Stormshield

1. Ouvrir la **Politique 10** → onglet **NAT**
2. Créer une nouvelle règle de **partage d'adresse source (masquerading)**
3. **Source originale** : `Network_internals`
4. **Destination originale** : `Internet`
5. **Interface de sortie** : `out`
6. **Source traduite** : `Firewall_Out` + port `ephemeral_fw` (aléatoire)
7. **Activer** la règle puis **Appliquer** la politique

!!! warning "Attention"
    Si la destination originale est laissée à `Any` au lieu de `Internet`, le pare-feu bloquera les flux d'administration (SSH/HTTPS) car ils seront traduits puis interprétés comme une tentative d'intrusion.

## Voir aussi

- [Architecture réseau (Mission 4)](../../missions/mission4.md)