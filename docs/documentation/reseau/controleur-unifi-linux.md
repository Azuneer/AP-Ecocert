# Fiche d'installation – Contrôleur UniFi OS Server sous Linux (Debian + Podman)

**Fiche rédigée par** : GADONNAUD Ewen & BOINA BOINA Rayan
**Formation** : BTS SIO 2ème année – Option SISR
**Établissement** : Lycée Paul-Louis Courier, Tours
**Contexte** : Ecocert GP3 – Mission 4 – serveur `WIFIECOCERT`
**Date** : Septembre 2026

> **Légende**
> - **[à vérifier]** : valeur à relever dans l’environnement utilisé ou point restant à confirmer à partir d’une source officielle.
> - Les prérequis et la procédure d'installation viennent de la documentation officielle Ubiquiti (§12). Les autres sources sont signalées.

---

## 1. Objectif

Installer sur une VM Debian du cluster Proxmox le contrôleur **UniFi OS Server** (qui embarque l'application UniFi Network), afin d'administrer la borne U6+.

| Paramètre  | Valeur                                         |
| ---------- | ---------------------------------------------- |
| Nom        | `WIFIECOCERT`                                  |
| IP         | `172.16.53.30` (fixe, VLAN 53, hors DHCP)      |
| Masque     | `255.255.255.0`                                |
| Passerelle | 172.16.53.253                                  |
| DNS        | `172.16.53.1` (`ADECOCERT`)                    |
| Conteneur  | Podman (imposé par UniFi OS Server sous Linux) |

## 2. Pourquoi Linux plutôt qu'une VM Windows

Selon la documentation officielle, l'installation sous Windows passe par WSL 2 (installé pendant la configuration) et n'est **pas prise en charge dans une VM invitée Hyper-V**. De plus, UniFi OS Server ne peut **pas** tourner comme service Windows. Sur Linux, il s'installe en une commande et se pilote avec `systemctl` (service `uosserver`).

## 3. Prérequis officiels

| Élément    | Exigence Ubiquiti                                                                                                                                                               |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Système    | Ubuntu 24.04 ou plus récent, **Debian 13 ou plus récent**, ou autre distribution récente avec systemd, libc 2.31+, **Podman 4.9.3+** (réseau « pasta ») et **slirp4netns 1.2+** |
| Processeur | x86-64                                                                                                                                                                          |
| RAM        | 2 Go minimum                                                                                                                                                                    |
| Disque     | 10 Go libres minimum                                                                                                                                                            |
| Réseau     | 100 Mbit/s filaire                                                                                                                                                              |
| Ports      | TCP 8080 et UDP 3478 (entre autres), à ouvrir                                                                                                                                   |

**Recommandation pour la VM**  : 2 vCPU, 4 Go de RAM, disque de 32 Go.

**Attention à la version de Debian.** Le minimum officiel est Debian 13. Sur une autre version, vérifier `podman --version` après l'installation : si Podman est en dessous de 4.9.3, l'installation peut échouer **[à vérifier]**. Le plus simple est de partir d'une **Debian 13**.

**À éviter :**
- **Cloner une VM** déjà utilisée : Ubiquiti déconseille de cloner les VM (les jetons d'accès distants seraient identiques). Créer une VM neuve.
- **Un conteneur LXC** : un test publié par un tiers indique que le réseau Podman fonctionne mal dans ce cas **[source tierce]**. Utiliser une VM KVM classique.

## 4. Étape 1 – Créer la VM dans Proxmox

1. Créer une VM (Debian 13, ISO netinst) avec les ressources du §3.
2. Carte réseau de la VM dans le **VLAN 53** : tag VLAN 53 sur la carte de la VM, ou bridge déjà dans le VLAN 53, selon la configuration de la ferme **[à vérifier]**.
3. Installer Debian en mode **serveur** (sans environnement graphique) : « serveur SSH » et « utilitaires usuels du système » suffisent.
4. Nom de machine : `wifiecocert`.

## 5. Étape 2 – IP fixe

Relever le nom de l'interface : `ip a` (souvent `ens18` sur une VM Proxmox **[à vérifier]**).

Sur une installation Debian classique, éditer `/etc/network/interfaces` :

```conf
auto ens18
iface ens18 inet static
    address 172.16.53.30/24
    gateway 172.16.53.253        # à remplacer par la vraie passerelle du VLAN 53
    dns-nameservers 172.16.53.1
```

Appliquer : `sudo systemctl restart networking` (ou redémarrer la VM). Si le système utilise NetworkManager, configurer la même IP avec `nmtui`.

Vérifications :
```bash
ip a                       # 172.16.53.30/24 sur l'interface
ping -c 3 <passerelle VLAN 53>
ping -c 3 172.16.53.1      # AD / DNS
ping -c 3 8.8.8.8          # Internet via le Stormshield (nécessaire pour télécharger l'installateur)
```

Ensuite, créer sur `ADECOCERT` un enregistrement A `wifiecocert` → `172.16.53.30` (et `unifi` → `172.16.53.30`, chemin de secours pour la découverte par les bornes).

## 6. Étape 3 – Installer Podman et les dépendances

Commande officielle Ubiquiti pour Debian/Ubuntu :

```bash
sudo apt-get update && sudo apt-get install podman slirp4netns
```

Ajouter `curl` (ou `wget`) si absent : `sudo apt-get install curl`.

Contrôle :
```bash
podman --version      # doit être 4.9.3 ou supérieur
```

## 7. Étape 4 – Télécharger et lancer l'installateur

1. Sur un poste avec navigateur, ouvrir la page de téléchargement Ubiquiti (<https://ui.com/download>) ou la page des versions (<https://community.ui.com/releases>). Choisir **UniFi OS Server, Linux x64**, faire un clic droit sur le téléchargement, **copier l'adresse du lien**. L'URL change à chaque version, ne pas réutiliser celle d'un tuto.
2. Sur la VM :
   ```bash
   curl -O <lien_copié>          # ou : wget <lien_copié>
   chmod +x <nom_du_fichier_téléchargé>
   sudo ./<nom_du_fichier_téléchargé>
   ```
3. Suivre les questions de l'installateur. L'installation télécharge et démarre le service.

Si la VM n'a pas d'accès Internet : télécharger l'installateur sur un poste, puis le copier avec `scp` vers la VM.

## 8. Étape 5 – Vérifier que le service tourne

Commandes officielles de gestion :

```bash
sudo systemctl status uosserver    # doit indiquer "active (running)"
sudo systemctl stop uosserver
sudo systemctl start uosserver
sudo systemctl enable uosserver    # démarrage automatique au boot
```

Vérifier les ports d'écoute :
```bash
sudo ss -tlnp | grep -E '11443|8080'
```

Selon une source tierce, l'installateur crée un utilisateur système `uosserver` qui exécute Podman : `sudo -u uosserver podman ps` liste alors le conteneur **[source tierce, à vérifier]**.

## 9. Étape 6 – Pare-feu de la VM

Debian n'active pas de pare-feu par défaut : en l’absence de pare-feu installé, aucun port n’est à ouvrir. Si `ufw` ou `nftables` est actif, autoriser au minimum les ports suivants (Ubiquiti cite TCP 8080 et UDP 3478 ; les autres viennent de sources tierces concordantes pour UniFi OS Server) :

| Port | Usage | Depuis |
|---|---|---|
| TCP 11443 | Interface web d'UniFi OS Server | Poste d'administration |
| TCP 8080 | Communication borne :left_right_arrow: contrôleur (inform) | VLAN 71 (borne) |
| UDP 3478 | STUN | VLAN 71 |
| UDP 10003 | Découverte pendant l'adoption | VLAN 71 |
| TCP 8444 | Portail invité (uniquement si portail captif) | VLAN 81 |

Exemple avec `ufw` :
```bash
sudo ufw allow OpenSSH
sudo ufw allow 11443/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 3478/udp
sudo ufw allow 10003/udp
sudo ufw enable
```

Pour une doc rigoureuse, croise cette liste avec la page officielle des ports : <https://help.ui.com/hc/en-us/articles/218506997-Required-Ports-Reference>.

## 10. Étape 7 – Première connexion et réglages

1. Depuis un poste d'administration : `https://172.16.53.30:11443`.
2. L’avertissement du navigateur concernant la confidentialité de la connexion est attendu avec un certificat auto-signé. Selon Ubiquiti, il peut être ignoré (on peut téléverser son propre certificat dans les paramètres du plan de contrôle).
3. Suivre l'assistant : créer le compte administrateur **local**. La gestion à distance via un compte Ubiquiti est **facultative** selon la doc officielle, et l'assistant peut la proposer : elle n'est pas nécessaire ici.
4. Nommer le site (par exemple « Ecocert GP3 »).
5. Régler l'**Inform Host** sur `172.16.53.30` : dans les paramètres de l'application Network, chercher « Inform Host » (l'emplacement change selon les versions) **[à vérifier]**. C'est cette adresse que les bornes utilisent pour joindre le contrôleur.
6. Laisser tourner le contrôleur en permanence : Ubiquiti précise qu'il doit rester en marche pour voir et gérer les équipements adoptés (s'il s'arrête, les bornes gardent leur dernière configuration).

## 11. Tests de validation (à capturer pour la recette)

| Test                        | Commande / méthode                                                               | Résultat attendu                       |
| --------------------------- | -------------------------------------------------------------------------------- | -------------------------------------- |
| IP fixe                     | `ip a`                                                                           | `172.16.53.30/24`                      |
| Joignabilité depuis le L3   | `ping 172.16.53.30` sur le L3                                                    | Réponse                                |
| Service actif               | `sudo systemctl status uosserver`                                                | `active (running)`                     |
| Ports ouverts               | `sudo ss -tlnp \| grep -E '11443\|8080'`                                         | Ports en écoute                        |
| Interface web               | Navigateur depuis un poste                                                       | Page de connexion / tableau de bord    |
| Joignable depuis le VLAN 71 | Depuis un poste du VLAN 71 : `nc -vz 172.16.53.30 8080` **[si `nc` disponible]** | Connexion réussie                      |
| Redémarrage                 | `sudo reboot`, puis nouveau test web                                             | Service redémarré tout seul (`enable`) |

Correspondance avec la fiche de recette : T-WF-01, T-WF-02, T-WF-03.

**Conseil :** après un premier fonctionnement propre, créer un **instantané (snapshot) Proxmox** de la VM. Un snapshot n'est pas un clone : il ne pose pas le problème des jetons dupliqués et permet de revenir en arrière si un test tourne mal.

## 12. Dépannage

| Symptôme | Causes probables | Vérifications |
|---|---|---|
| L'installateur refuse de démarrer ou échoue | Podman trop ancien, `slirp4netns` absent, Debian < 13 | `podman --version` (≥ 4.9.3), `apt-get install slirp4netns`, version de Debian |
| Erreur liée au réseau « pasta » | Composant absent | Vérifier les dépendances de Podman ; en cas de doute, installer le paquet `passt` **[hypothèse à tester, non confirmée par Ubiquiti]** |
| Téléchargement impossible | Pas d'Internet sur la VM | `ping 8.8.8.8` ; route par défaut ; NAPT du Stormshield |
| L'URL de l'installateur ne marche plus | Version obsolète | Recopier le lien depuis la page officielle |
| Interface web inaccessible | Service arrêté ; pare-feu ; mauvais port | `systemctl status uosserver`, `ss -tlnp`, pare-feu de la VM, URL en `https://...:11443` |
| Les bornes ne voient pas le contrôleur | VLAN 71 non routé ; TCP 8080 bloqué ; Inform Host incorrect | Ping depuis le L3 ; règles de pare-feu ; réglage de l'Inform Host |
| Contrôleur inaccessible après redémarrage | Service non activé | `sudo systemctl enable uosserver` |

## 13. Sources et niveau de fiabilité

**Source officielle Ubiquiti** (fiabilité élevée)
- Self-Hosting UniFi (prérequis, installation Linux, commandes `systemctl`, note sur les clones de VM, FAQ) : <https://help.ui.com/hc/en-us/articles/34210126298775-Self-Hosting-UniFi>
- Ports requis : <https://help.ui.com/hc/en-us/articles/218506997-Required-Ports-Reference>
- Adoption d'équipements (remote adoption) : <https://help.ui.com/hc/en-us/articles/360012622613-UniFi-Device-Adoption>

**Sources tierces** (fiabilité moyenne, à recouper)
- Ports d'UniFi OS Server (11443 en pratique, 10003 pour la découverte) : <https://www.unihosted.com/blog/changing-the-unifi-controller-port-a-step-by-step-guide> et <https://github.com/lemker/unifi-os-server>
- Utilisateur `uosserver` et commandes Podman : <https://www.unihosted.com/blog/how-to-install-unifi-os-server-on-linux>
- Limite LXC / Podman : <https://www.virtualizationhowto.com/2025/08/new-unifi-os-server-lets-you-self-host-the-full-unifi-experience/>
- Exemple d'installation sur Debian avec Podman : <https://www.crosstalksolutions.com/complete-unifi-os-server-installation-on-linux-best-practices/>

**Correction par rapport à mes fiches précédentes** : j'avais indiqué « Podman 4.3.1 ou supérieur » et « 2 vCPU, 4 Go de RAM, 25 Go » d'après des guides tiers plus anciens. La documentation officielle (prérequis du §3) fait foi : Podman 4.9.3+, 2 Go de RAM minimum, 10 Go libres, Debian 13+.

**Points non vérifiés**
- Version de Debian et de Podman réellement disponibles dans l’environnement utilisé.
- Emplacement exact du réglage « Inform Host » dans la version utilisée de l'interface.
- Nom de l'interface réseau de la VM et méthode de tag VLAN dans la ferme Proxmox.
- Nécessité éventuelle du paquet `passt`.
