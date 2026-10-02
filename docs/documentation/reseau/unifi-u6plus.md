# Fiche de procédure – Installation de la borne UniFi U6+ dans le réseau segmenté Ecocert GP3

**Fiche rédigée par** : GADONNAUD Ewen & BOINA BOINA Rayan
**Formation** : BTS SIO 2ème année – Option SISR
**Établissement** : Lycée Paul-Louis Courier, Tours
**Contexte** : Ecocert GP3 – Mission 4
**Date** : Septembre 2026
**Version** : v2 (adaptée à l'architecture réelle du groupe)

> **Légende**
> - **[à valider]** : choix non imposé par le sujet, ou comportement à confirmer par un test.
> - **[à vérifier]** : valeur ou état à relever sur l'équipement avant de configurer.
> - Sources en fin de document (§14).

---

## 1. Ce qu'on veut obtenir

Une borne Wi-Fi UniFi U6+ qui diffuse **deux SSID**, chacun placé dans un VLAN du plan d'adressage :

| SSID | VLAN | Réseau | Passerelle |
|---|---|---|---|
| `Service-Technique` | 71 | `192.168.3.192/28` | `192.168.3.206` |
| `Wifi-Visiteurs` | 81 | `192.168.3.96/27` | `192.168.3.126` |

La borne est administrée depuis le réseau Serveurs par le contrôleur `WIFIECOCERT` (`172.16.53.30`). Les SSID sont protégés par WPA2 ou WPA3 avec la clé partagée du sujet (non reproduite dans ce document).

## 2. Décisions prises pour GP3

| #   | Décision                                                                                                           | Statut        |
| --- | ------------------------------------------------------------------------------------------------------------------ | ------------- |
| 1   | La borne est branchée sur le **port 40 du switch L2**, configuré en **trunk**                                      | Décidé        |
| 2   | Alimentation par **injecteur PoE**, placé entre le switch et la borne                                              | Décidé        |
| 3   | **VLAN natif du port = 53** : la borne prend son IP de gestion dans le VLAN 53                                     | Décidé        |
| 4   | VLAN **tagués** sur le trunk : 71 et 81                                                                            | Décidé        |
| 5   | Le contrôleur reste en **IP fixe** dans le VLAN 53 (hors DHCP)                                                     | Décidé        |
| 6   | Le **DHCP existant du VLAN 53** distribue les IP des VLAN 71 et 81 via le **relais DHCP déjà configuré** sur le L3 | Déjà en place |
| 7   | **Option 43** ajoutée dans le scope du **VLAN 53 uniquement**                                                      | À faire       |
| 8   | UniFi ne fait ni routage ni DHCP : les réseaux sont déclarés en **passerelle tierce** (Cisco L3)                   | Décidé        |
|     |                                                                                                                    |               |

## 3. Vue d'ensemble

```
                 VLAN 53 (Serveurs, IP fixes)
   ┌────────────────────────────────────────────┐
   │ ADECOCERT    172.16.53.1   (AD + DNS)      │
   │ DHCPECOCERT  172.16.53.2   (DHCP)          │
   │ WIFIECOCERT  172.16.53.30  (Contrôleur)    │
   └───────────────────────┬────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Cisco L3   │  SVI Vlan71 (.206) + helper-address 172.16.53.2
                    │   (9200)    │  SVI Vlan81 (.126) + helper-address 172.16.53.2
                    └──────┬──────┘
                           │ trunk (L3 port 23 ↔ L2 port 48), VLAN 71 et 81 autorisés
                    ┌──────┴──────┐
                    │  Cisco L2   │
                    │   (2960)    │  port 40 = TRUNK (natif 53, tagués 71 + 81)
                    └──────┬──────┘
                           │ câble RJ-45
                    [IN] INJECTEUR PoE [OUT]
                           │ câble RJ-45 (données + alimentation)
                    ┌──────┴──────┐
                    │ Borne U6+   │  IP de gestion : VLAN 53 (non tagué)
                    │             │  SSID Service-Technique → VLAN 71 (tagué)
                    │             │  SSID Wifi-Visiteurs    → VLAN 81 (tagué)
                    └─────────────┘
```

## 4. Les confusions classiques, expliquées une fois pour toutes

### 4.1 « Le DHCP est dans le VLAN 53, comment peut-il distribuer des IP dans les VLAN 71 et 81 ? »

Grâce au **relais DHCP** (`ip helper-address 172.16.53.2`) configuré sur les interfaces VLAN du L3 (déjà fait).

1. Le client (ou la borne) envoie un DHCPDISCOVER en **broadcast** ; il reste dans son VLAN et arrive à la SVI du L3.
2. La SVI le transforme en **unicast** vers `172.16.53.2`, en y inscrivant sa propre IP (champ `giaddr` : `192.168.3.206` pour le VLAN 71, `192.168.3.126` pour le VLAN 81).
3. Le serveur lit le `giaddr`, en déduit le sous-réseau et choisit le **scope correspondant**.
4. Il répond au relais, qui transmet la réponse au client.

Conséquence : il faut **un scope par sous-réseau** sur le serveur, avec la bonne passerelle. Sans scope correspondant au `giaddr`, la requête est ignorée. Le VLAN 53 n'a pas de scope (adressage statique voulu par le sujet).

### 4.2 « Un port de switch appartient à un VLAN, non ? »

Pas un port **trunk**. Un port *access* appartient à un seul VLAN (poste filaire). Un port *trunk* transporte **plusieurs VLAN étiquetés** (802.1Q). La borne diffuse deux SSID dans deux VLAN différents avec un seul câble : elle a donc besoin d'un trunk. L'emplacement du port (bloc coloré du plan de câblage) n'a aucune importance technique : seule sa configuration compte.

### 4.3 « C'est quoi le VLAN natif ? »

Sur un trunk, tout est tagué **sauf un VLAN : le VLAN natif**, qui circule sans tag.

- Le trafic de **gestion de la borne** (sa propre IP, son DHCP, son contact avec le contrôleur) est **non tagué** : il tombe dans le VLAN natif du port.
- Le trafic des **clients Wi-Fi** est **tagué** selon le VLAN de leur SSID.

D'où le choix : natif = **71**, parce que ce VLAN a un DHCP, une passerelle, une route vers le contrôleur, et qu'il correspond aux administrateurs réseau. Par défaut, une borne UniFi utilise le VLAN 1 pour joindre son contrôleur sauf réglage contraire dans ses paramètres IP.

### 4.4 « L'IP de la borne et l'IP des clients, c'est la même chose ? »

Non.
- **IP de gestion de la borne** : `192.168.3.193-.205` (scope VLAN 71), obtenue en DHCP, non taguée.
- **IP des clients Wi-Fi** : dépend du SSID (VLAN 71 ou 81).

### 4.5 « Où va l'option 43 ? »

Dans le **serveur DHCP**, dans le **scope du VLAN 71** uniquement (là où la borne prend son IP). Ce n'est pas le relais du L3 qui l'ajoute : il ne fait que faire passer la réponse. Le VLAN 81 n'en a pas besoin.

### 4.6 « UniFi va-t-il faire du DHCP ou du routage ? »

Non. Dans le contrôleur, les réseaux sont déclarés avec le type **passerelle tierce** (Third-party Gateway). Le contrôleur ne fait que rattacher chaque SSID à un **VLAN ID**. Le routage reste sur le Cisco L3, le DHCP sur `DHCPECOCERT`.

### 4.7 « Le pare-feu Stormshield est-il dans le chemin borne → contrôleur ? »

Non. Le trafic VLAN 71 → VLAN 53 est routé par le **L3**. Le Stormshield n'intervient que pour la **sortie vers WAN-SIO** (NAPT). Seules d'éventuelles ACL sur le L3 ou le pare-feu du serveur du contrôleur peuvent bloquer la borne.

### 4.8 « Le contrôleur doit-il avoir une IP fixe ? »

Oui : `172.16.53.30`, masque `255.255.255.0`, DNS `172.16.53.1`. Cette IP est **hors DHCP** (le VLAN 53 est statique) donc pas de conflit. La **passerelle** est à relever sur la SVI `Vlan53` du L3 **[à vérifier]** : les documents de référence divergent (`172.16.53.254` sur le schéma logique, `172.16.53.253` dans la table de routage).

### 4.9 « Que deviennent les ports 37-39 du L2 (bloc Wifi-Visiteurs) ? »

Ils ne servent plus au Wi-Fi : les visiteurs passent par la borne. Deux choix :
- accès filaire visiteurs voulu : les garder en accès VLAN 81 et le **documenter** (accolade du plan raccourcie à 37-39) ;
- sinon : `shutdown` et retirer du plan.

Les laisser actifs ne casse rien, mais un poste branché obtiendrait une IP du VLAN 81 sans clé Wi-Fi. Les ports jamais configurés (VLAN 1 par défaut) sont plus risqués : les éteindre est une bonne pratique. Les ports 31-34 (VLAN 71 filaire) restent utiles.

### 4.10 « Injecteur PoE : quel câble où ? »

Voir §6. En bref : `switch → IN`, `OUT → borne`, secteur en dernier. Ne jamais brancher `OUT` sur autre chose que la borne.

## 5. Prérequis (à cocher avant de commencer)

- [ ] Contrôleur `WIFIECOCERT` installé, IP fixe `172.16.53.30`, compte admin créé
- [ ] Ping du L3 vers `172.16.53.30` : réponse
- [ ] SVI `Vlan71` (`192.168.3.206`) et `Vlan81` (`192.168.3.126`) en `up/up` avec `ip helper-address 172.16.53.2`
- [ ] Scopes DHCP VLAN 71 et VLAN 81 présents sur `DHCPECOCERT`
- [ ] Trunk L2 :left_right_arrow: L3 (L3 port 23 :left_right_arrow: L2 port 48) autorise les VLAN 71 et 81
- [ ] Injecteur PoE + 2 câbles RJ-45 disponibles
- [ ] Clé Wi-Fi du sujet sous la main
- [ ] Documentation d'état relevée (§13)

## 6. Étape 1 – Câblage physique avec injecteur PoE

```
Switch L2 (port 40) ──câble──▶ [IN / LAN]  INJECTEUR  [OUT / POE] ──câble──▶ Borne U6+
                                                │
                                         cordon secteur
```

1. **Switch → injecteur** : câble RJ-45 du port 40 vers l'entrée `IN` (ou `LAN`) de l'injecteur. Cette entrée ne transporte que les données.
2. **Injecteur → borne** : câble RJ-45 de la sortie `OUT` (ou `POE`) vers l'unique port de la borne. Ce câble transporte données **et** alimentation.
3. **Cordon secteur** de l'injecteur : branché **en dernier**.

> **Attention** : ne jamais brancher la sortie `OUT/POE` sur un switch, un PC ou un autre équipement, elle envoie du courant sur le câble.

Notes :
- La U6+ est alimentée en PoE 802.3af (15 W) ou en 48 V passif, et l'injecteur n'est pas fourni avec la borne ; vérifier la référence et la tension marquées sur l'étiquette de l'injecteur.
- L'injecteur laisse passer les données telles quelles : le trunk fonctionne comme avec un câble direct.
- Comme l'injecteur alimente la borne, le port 40 n'a pas besoin de fournir de PoE.

## 7. Étape 2 – Configuration du switch L2 (Cisco 2960)

Relever d'abord l'état du port : `show running-config interface FastEthernet0/40` (ou `GigabitEthernet0/40`, selon le modèle, vérifier avec `show interfaces status`).

```cisco
! Création des VLAN s'ils n'existent pas
vlan 71
 name SERVICES-TECHNIQUES
vlan 81
 name WIFI-VISITEURS

! Port de la borne (ancien port accès VLAN 81 → trunk)
interface FastEthernet0/40
 description AP-UNIFI-U6PLUS
 no switchport access vlan 81
 switchport mode trunk
 switchport trunk native vlan 71
 switchport trunk allowed vlan 71,81
 spanning-tree portfast trunk
 no shutdown

! Liaison montante vers le L3 (port 48 selon le plan de câblage)
interface FastEthernet0/48
 switchport mode trunk
 switchport trunk allowed vlan add 71,81
```

Vérifications :
- `show interfaces trunk` : port 40 en trunk, natif 71 ; VLAN 71 et 81 autorisés **et actifs** sur le port 48.
- Le VLAN natif du port est **le même des deux côtés** d'un trunk, sinon le switch signale un décalage de VLAN natif.
- `show interfaces status` : le port 40 passe en `connected` une fois la borne alimentée.

Ports inutilisés (§4.9) :
```cisco
interface range FastEthernet0/38 - 39
 shutdown
```
(à adapter selon la décision prise pour les ports 37-39)

## 8. Étape 3 – Vérifier le L3 (Cisco 9200)

Le relais est déjà configuré. Contrôler seulement :

```cisco
show ip interface brief
show running-config interface Vlan71
show running-config interface Vlan81
show interfaces trunk
ping 172.16.53.30
```

Attendu : SVI `up/up`, `ip helper-address 172.16.53.2` présent, VLAN 71 et 81 autorisés sur le trunk vers le L2, ping du contrôleur OK.

Si des ACL existent : autoriser depuis le VLAN 71 vers `172.16.53.30` **TCP 8080** et **UDP 3478**.

## 9. Étape 4 – Contrôleur `WIFIECOCERT` (VLAN 53)

Le sujet demande un contrôleur « Unifi OS » sur Debian ou Windows Server. Deux produits existent, avec des ports d'interface web différents :

| Produit | Interface web (TCP) | Inform borne (TCP) |
|---|---|---|
| UniFi Network Server (historique) | 8443 | 8080 |
| UniFi OS Server (auto-hébergé) | 11443 en pratique | 8080 |

Points de contrôle (Debian) :
- IP fixe `172.16.53.30` **[à vérifier]** passerelle : voir §4.8.
- UniFi OS Server sous Linux s'appuie sur **Podman** (4.3.1 ou supérieur) : `podman --version`. Ressources relevées dans un guide tiers pour Ubuntu : 2 vCPU, 4 Go de RAM, 25 Go libres minimum.
- Installateur à télécharger depuis le site officiel Ubiquiti (l'URL change à chaque version).
- **Inform Host** : dans les paramètres du contrôleur, régler sur `172.16.53.30` (chercher « Inform »). L'emplacement change selon les versions.

Ports à autoriser vers le contrôleur (pare-feu hôte, ACL éventuelles) :

| Sens | Port | Usage |
|---|---|---|
| Borne → contrôleur | TCP 8080 | Communication borne :left_right_arrow: contrôleur (inform) : **indispensable** |
| Borne :left_right_arrow: contrôleur | UDP 3478 | STUN |
| Borne → contrôleur | UDP 10001 (Network Server) / 10003 (OS Server) | Découverte pendant l'adoption |
| Admin → contrôleur | TCP 8443 ou 11443 | Interface web |
| Borne → contrôleur | TCP 8880-8882, 8843 | Portail invité (uniquement si portail captif) |

## 10. Étape 5 – DHCP : option 43 dans le scope VLAN 71

### 10.1 Principe

Le DHCP renvoie à la borne l'adresse du contrôleur dans l'**option 43** (sous-option 1). La borne s'identifie avec le vendor class `ubnt`. Encodage : `01` (sous-option) + `04` (longueur) + IP en hexadécimal.

| Contrôleur | Hexadécimal | Valeur option 43 |
|---|---|---|
| `172.16.53.30` | AC . 10 . 35 . 1E | `01:04:AC:10:35:1E` (soit `0104AC10351E`) |

### 10.2 Serveur ISC DHCP (`/etc/dhcp/dhcpd.conf`)

```conf
option space ubnt;
option ubnt.unifi-address code 1 = ip-address;

class "ubnt" {
    match if substring (option vendor-class-identifier, 0, 4) = "ubnt";
    option vendor-class-identifier "ubnt";
    vendor-option-space ubnt;
}

subnet 192.168.3.192 netmask 255.255.255.240 {      # VLAN 71
    range 192.168.3.193 192.168.3.205;
    option routers 192.168.3.206;
    option domain-name-servers 172.16.53.1;
    option ubnt.unifi-address 172.16.53.30;         # IP du contrôleur
}
```

Contrôle : `dhcpd -t -cf /etc/dhcp/dhcpd.conf`, puis `systemctl restart isc-dhcp-server`.

### 10.3 Serveur Kea DHCPv4 (`/etc/kea/kea-dhcp4.conf`)

```json
{
  "Dhcp4": {
    "option-def": [
      { "space": "ubnt", "name": "unifi-address", "code": 1, "type": "ipv4-address" }
    ],
    "client-classes": [
      {
        "name": "ubnt",
        "test": "substring(option[60].hex,0,4) == 'ubnt'",
        "option-data": [
          { "space": "dhcp4", "name": "vendor-class-identifier", "code": 60, "data": "ubnt" },
          { "name": "vendor-encapsulated-options", "code": 43 }
        ],
        "option-def": [
          { "name": "vendor-encapsulated-options", "code": 43, "type": "empty", "encapsulate": "ubnt" }
        ]
      }
    ],
    "subnet4": [
      {
        "id": 71,
        "subnet": "192.168.3.192/28",
        "pools": [ { "pool": "192.168.3.193 - 192.168.3.205" } ],
        "option-data": [
          { "name": "routers", "data": "192.168.3.206" },
          { "name": "domain-name-servers", "data": "172.16.53.1" },
          { "space": "ubnt", "name": "unifi-address", "code": 1, "data": "172.16.53.30" }
        ]
      }
    ]
  }
}
```

Contrôle : `kea-dhcp4 -t /etc/kea/kea-dhcp4.conf`. **[à valider]** la syntaxe peut varier selon la version de Kea : si l'option n'apparaît pas dans la capture (§12), consulter la documentation de la version installée.

### 10.4 Chemin de secours DNS

Créer sur `ADECOCERT` un enregistrement A `unifi` → `172.16.53.30`. Des retours de terrain indiquent que certaines versions de firmware tentent `http://unifi:8080/inform` en dernier recours. Le suffixe DNS (`local.ecocert3.fr`) doit être distribué par le DHCP pour que le nom court soit résolu.

### 10.5 Dimensionnement du scope VLAN 71

13 adresses hors passerelle (`.193` à `.205`) pour 10 hôtes prévus (12 avec la marge de 20 %). **La borne consomme une adresse** : il reste 12 adresses pour les postes. Une réservation DHCP par adresse MAC de la borne est possible (facultatif).

## 11. Étape 6 – Adoption puis configuration des SSID

### 11.1 Mise sous tension et IP de la borne

1. Vérifier le câblage (§6) et brancher l'injecteur au secteur.
2. La borne démarre et envoie sa requête DHCP (vendor class `ubnt`). Elle doit recevoir une IP entre `192.168.3.193` et `.205`, la passerelle `.206`, et l'option 43.
3. Contrôler le bail dans les journaux du serveur DHCP. Avec ISC : `DHCPDISCOVER from <MAC> via 192.168.3.206`.

### 11.2 Adoption

**Méthode nominale (option 43 correcte)** : la borne apparaît en **attente d'adoption** dans le contrôleur, cliquer sur **Adopter** (libellé et menu variables selon la version). Laisser le contrôleur provisionner la borne et proposer la mise à jour du firmware.

**Méthode de secours (`set-inform`)** : si la borne n'apparaît pas au bout d'environ 10 minutes, ne pas s'acharner sur l'option 43.

1. Relever l'IP de la borne dans les baux DHCP.
2. Connexion SSH à la borne. Identifiants par défaut avant adoption : `ubnt` / `ubnt` (certaines sources indiquent `ui` / `ui` pour des équipements plus récents : tester les deux).
3. Exécuter : `set-inform http://172.16.53.30:8080/inform`
4. La borne apparaît dans le contrôleur : l'adopter.
5. Selon la documentation Ubiquiti, il peut falloir **répéter la commande** une fois la borne apparue dans l'interface.

La commande `info` sur la borne affiche l'URL d'inform actuellement configurée. Après adoption, les identifiants SSH sont redéfinis par le contrôleur.

### 11.3 Réseaux dans le contrôleur

Les VLAN existent déjà sur la passerelle (le L3 Cisco). Dans le contrôleur : Paramètres → Réseaux → Créer un réseau.

| Nom | Routeur | VLAN ID |
|---|---|---|
| Services-Techniques | Passerelle tierce (Third-party Gateway) | 71 |
| WiFi-Visiteurs | Passerelle tierce (Third-party Gateway) | 81 |

Utiliser **les mêmes VLAN ID** que sur le L3.

### 11.4 SSID

Paramètres → WiFi → Créer :

| SSID | Réseau associé | Sécurité |
|---|---|---|
| `Service-Technique` | Services-Techniques (VLAN 71) | WPA2 ou WPA3 Personnel, clé du sujet |
| `Wifi-Visiteurs` | WiFi-Visiteurs (VLAN 81) | WPA2 ou WPA3 Personnel, clé du sujet |

Sélectionner la borne comme diffuseur. Si les VLAN ne sont pas autorisés sur tout le chemin borne → passerelle, les clients ne peuvent pas rejoindre le Wi-Fi.

> Ne pas écrire la clé Wi-Fi dans ce document ni dans la fiche de recette : la référencer comme « clé du sujet ».

## 12. Étape 7 – Vérifications et point de vigilance

| Vérification               | Commande / méthode                                               | Résultat attendu                                            |
| -------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| Trunk actif                | `show interfaces trunk` (L2 et L3)                               | Port 40 trunk, natif 71 ; 71 et 81 autorisés sur le port 48 |
| Port de la borne actif     | `show interfaces status`                                         | `connected`                                                 |
| Relais DHCP                | `show running-config interface Vlan71`                           | `ip helper-address 172.16.53.2`                             |
| Bail de la borne           | Journaux du serveur DHCP                                         | IP dans `192.168.3.193-.205`                                |
| Option 43 émise            | Sur le serveur DHCP : `tcpdump -i any -n -vv port 67 or port 68` | Réponse avec « Vendor-Option 43 » et l'IP du contrôleur     |
| Borne joint le contrôleur  | Ping depuis le L3, TCP 8080 non bloqué                           | Réponse                                                     |
| Borne adoptée              | Interface du contrôleur                                          | État « connecté »                                           |
| Client `Service-Technique` | Connexion d'un terminal                                          | IP en `192.168.3.192/28`, passerelle `.206`                 |
| Client `Wifi-Visiteurs`    | Connexion d'un terminal                                          | IP en `192.168.3.96/27`, passerelle `.126`                  |
| Sortie Internet            | Ping `8.8.8.8` depuis chaque client                              | Réponse (NAPT du Stormshield)                               |

**Point de vigilance [à valider]** : le VLAN 71 est à la fois natif du port et VLAN d'un SSID. Le comportement de la borne dans ce cas reste à confirmer à partir d’une source fiable. Si un client du SSID `Service-Technique` reçoit une mauvaise IP ou aucune, c'est la première piste. Plan B : un **VLAN de gestion dédié**, non utilisé par un SSID, pris dans la réserve `192.168.3.224/27` de la Mission 1 (nouvelle SVI, nouveau scope avec option 43, natif du port 40 à changer). À faire valider par l'enseignant. Plafonner le dépannage de ce point à 20 minutes ; au-delà, documenter l'anomalie dans la fiche de recette.

## 13. Documentation à mettre à jour

Relever d'abord l'état réel des équipements :
- `show ip interface brief` sur le L3 : IP de la SVI `Vlan53` et passerelles des autres VLAN ;
- interface OUT du Stormshield : IP WAN réelle (`172.16.32.3` ou `172.16.32.13`) ;
- `show interfaces trunk` (L2 et L3) : VLAN réels sur la liaison L3 port 23 :left_right_arrow: L2 port 48, et ID du VLAN du lien pare-feu (« VLAN 55 » sur le schéma physique).

| Document | Correction |
|---|---|
| Schéma logique | Lien VLAN 81 : `192.168.3.126/25` → `/27` ; IP WAN du pare-feu et passerelle VLAN 53 alignées sur l'état réel |
| Schéma physique | Borne reliée aux VLAN 71 et **81** (le PDF affichait 61) ; libellé du trunk : `11,21,31,41,61,71,81` ; supprimer ou remplacer « VLAN 10 CLIENT » ; ajouter le port 40 du L2 comme lien vers la borne ; vérifier l'ID du « VLAN 55 » |
| Plan de câblage | Port 40 « BORNE WIFI (TRUNK : natif 71, tagué 81) » ; borne Unifi U6+ et injecteur PoE ; accolade « WIFIVISITEURS » selon la décision §4.9 ; **réexporter le PDF** (titre « ECOCERT ») |
| Table de routage L3 | Remplacer les deux lignes VLAN 31 par `192.168.3.160 255.255.255.224` via `192.168.3.190` ; ajouter VLAN 41 : `192.168.3.208 255.255.255.240` via `192.168.3.222` ; passerelle VLAN 53 alignée sur la SVI |
| Tables de routage pare-feu et NAT | IP WAN du Stormshield alignée sur l'état réel dans les deux documents |
| Fiche de recette | Cocher la section 4 au fur et à mesure ; compléter T-WF-05 avec l'IP de gestion de la borne (VLAN 71) |

## 14. Plan de la séance (4 h)

| Temps | Étape | Critère de sortie |
|---|---|---|
| 0:00 – 0:45 | Contrôleur (§9) | Interface web accessible |
| 0:45 – 1:05 | Réseau : L3, trunk port 48, option 43 (§8, §10) | Ping OK, trunk correct |
| 1:05 – 1:20 | Port 40 en trunk, câblage avec injecteur (§6, §7) | La borne prend une IP |
| 1:20 – 1:45 | Adoption (§11.2) | Borne « connectée » |
| 1:45 – 2:15 | Réseaux et SSID (§11.3, §11.4) | Deux SSID diffusés |
| 2:15 – 2:50 | Tests clients (§12) | Bonnes plages IP, Internet |
| 2:50 – 4:00 | Recette et documentation | Livrables complets |

Conseils : une capture par test au moment où on le fait ; plafonner chaque blocage à 20 minutes ; en cas de blocage sur le contrôleur, prévenir l'enseignant tôt.

## 15. Dépannage

| Symptôme | Causes probables | Vérifications |
|---|---|---|
| La borne ne s'allume pas | Injecteur mal branché (câbles inversés), injecteur non alimenté | IN côté switch, OUT côté borne, secteur branché |
| Pas d'IP pour la borne | VLAN natif incorrect ; VLAN absent du trunk ; relais DHCP ; scope manquant | `show interfaces trunk`, `ip helper-address`, journaux DHCP |
| IP obtenue mais borne absente du contrôleur | Option 43 absente ou mal formée ; TCP 8080 bloqué ; pas de route | Capture DHCP (§12) ; `set-inform` ; ACL / pare-feu hôte |
| Adoption bloquée | Inform Host incorrect ; commande à répéter | Vérifier l'Inform Host ; relancer `set-inform` |
| Clients connectés sans IP | VLAN du SSID non autorisé sur le trunk ; `helper-address` absent ; scope manquant | `show interfaces trunk`, SVI, scope DHCP |
| Clients avec l'IP du mauvais VLAN | Décalage VLAN natif ; association SSID → réseau incorrecte | Natif identique des deux côtés ; réseau du SSID ; point de vigilance §12 |
| Clients avec IP mais sans Internet | Routage / NAPT | Route par défaut du L3 vers `192.168.33.254` ; règle NAT du Stormshield |
| Le trunk du port 48 ne transporte pas 71/81 | VLAN non autorisés ou non créés | `switchport trunk allowed vlan add 71,81` des deux côtés |

## 16. Sources et niveau de fiabilité

**Sources officielles Ubiquiti** (fiabilité élevée)

- Adoption couche 3 (SSH, option 43, DNS) : <https://help.ui.com/hc/en-us/articles/204909754-UniFi-Layer-3-Methods-for-UAP-Adoption-and-Management>
- Adoption à distance, encodage de l'option 43 (préfixe `0104` + IP en hexadécimal) : <https://help.ui.com/hc/en-us/articles/204909754-Remote-Adoption-Layer-3>
- Adoption d'équipements, cas VLAN / sous-réseau différent : <https://help.ui.com/hc/en-us/articles/360012622613-UniFi-Device-Adoption>
- Création de SSID et association aux VLAN (VLAN 1 par défaut pour la gestion, trunk recommandé) : <https://help.ui.com/hc/en-us/articles/26136823938583-Creating-UniFi-WiFi-SSIDs>
- VLAN avec passerelle tierce : <https://help.ui.com/hc/en-us/articles/9761080275607-Creating-Virtual-Networks-VLANs>
- Ports requis : <https://help.ui.com/hc/en-us/articles/218506997-Required-Ports-Reference>

**Sources communautaires et tierces** (fiabilité moyenne, recoupées entre elles)

- Exemples ISC DHCP et Cisco (`option 43 hex`) : <https://www.techfortechs.com/index.php?topic=35.0> et <https://jnicolson.blogspot.com/2016/03/unifi-ap-dhcp-option-43.html>
- Exemple Kea (client class `ubnt`) : <https://www.mail-archive.com/kea-users@lists.isc.org/msg04384.html>
- Option 43 UniFi, chemin DNS de secours : <https://tcpip.wtf/en/unifi-l3-adoption-with-dhcp-option-43-on-pfsense-mikrotik-and-others.htm> et <https://vdaluz.com/blog/third-ap-dhcp-option-43-adoption>
- Cas Cisco 9200 / UniFi / VLAN natif et DHCP distant : <https://community.cisco.com/t5/switching/vlan-trunk-and-native-vlan-dhcp-issue/td-p/4863320>
- UniFi OS Server sur Linux (Podman, ports) : <https://lazyadmin.nl/home-network/unifi-os-server/> et <https://www.unihosted.com/blog/changing-the-unifi-controller-port-a-step-by-step-guide>
- Caractéristiques U6+ (PoE 802.3af, injecteur non fourni) : <https://www.netxl.com/wifi-access-points/ubiquiti-unifi-u6-plus-wifi-6-access-point/>
- Injecteur 802.3af Ubiquiti (15 W, 48 V) : <https://prod.cy-wireless.com/u-poe-af-el>

**Points non vérifiés dans des sources primaires**

- Syntaxe exacte de la configuration Kea pour la version installée.
- Comportement de la borne lorsque le VLAN d'un SSID est identique au VLAN natif du port.
- Emplacement exact des menus du contrôleur, qui change selon les versions.
- Ressources minimales du serveur pour UniFi OS Server sur Debian (valeurs relevées sur un guide Ubuntu tiers).
- Alimentation exacte de l'injecteur fourni (à lire sur son étiquette).
