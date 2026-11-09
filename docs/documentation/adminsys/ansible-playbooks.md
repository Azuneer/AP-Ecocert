# ECOCERT — comprendre le code des playbooks Ansible

> :bust_in_silhouette: **Fiche rédigée par** : GADONNAUD Ewen  
> :mortar_board: **Formation** : BTS SIO 2ème année - Option SISR  
> :school: **Établissement** : Lycée Paul-Louis Courier, Tours  
> :calendar: **Date** : Novembre 2026

Documentation du kit `ansible-ecocert-vlan53`, révisée le 9 novembre 2026.

[Compte rendu de la situation professionnelle 3](../../missions/sp3-ansible.md) · [Fonctionnement d’Ansible](ansible.md) · [Kit documentaire des playbooks](../../assets/situations/sp3-ansible/ansible-ecocert-vlan53.zip)


## Repères de lecture

- Sections 1–3 : environnement, lecture du YAML, inventaire et variables.
- Section 4 : contrôles préalables, playbook 00.
- Section 5 : clés et configuration SSH, playbook 01.
- Section 6 : applications, playbook 02.
- Section 7 : mises à jour à la demande, playbook 03.
- Section 8 : politique de mots de passe et expressions régulières PAM, playbook 04.
- Section 9 : mises à jour périodiques, playbook 05.
- Sections 10–12 : regroupement site.yml, lecture des résultats et preuves à produire.

## 1. Périmètre et environnement

Ce document reprend le code des fichiers fournis et explique ce que chaque tâche fait, les paramètres utilisés et les limites à connaître. Il ne constitue pas un compte rendu de déploiement intégral.

| Machine | Adresse | Rôle |
|---|---|---|
| SRVANSIBLE | `172.16.53.10/24` | Contrôleur depuis lequel etudiant lance Ansible |
| CLIENTANSIBLE | `172.16.53.151/24` | Client Debian 13 Cinnamon à administrer |

Les deux VM sont placées dans le VLAN 53 pour ce prototype. La passerelle retenue est `172.16.53.253`, et le DNS indiqué par Ewen est `8.8.8.8`. Les interfaces sont configurées séparément avec le gestionnaire réseau effectivement utilisé sur chaque VM : les playbooks ne changent ni l'adressage, ni le DNS, ni le hostname des VM.

**Écarts au sujet :** le sujet initial demande un serveur nommé CONFECOCERT et une recette sur un client du VLAN Formations professionnelles. Le laboratoire utilise le nom SRVANSIBLE et place temporairement le client dans le VLAN Serveurs. Ces adaptations doivent être signalées dans le dossier.

### État des vérifications

Les captures du compte rendu montrent Debian **13.4**, la réussite des contrôles initiaux et l’exécution des playbooks 01 à 05. Les récapitulatifs visibles de 00, 02, 03, 04 et 05 indiquent `failed=0` et `unreachable=0`. Le diff de 01 confirme la configuration et le rechargement SSH, avec l’assertion finale réussie ; son récapitulatif est coupé.

Une connexion par clé est visible avant le déploiement SSH ; un nouvel essai après celui-ci reste à conserver. Les refus de mots de passe faibles suivis d’un changement accepté sont documentés. L’avertissement sudo sur la résolution du nom `CLIENTANSIBLE` reste à corriger. Les timers sont présents ; aucun journal ne démontre encore une exécution périodique après le déploiement.

La version **ansible-core 2.19.11** est celle déclarée dans les notes de séance ; la sortie `ansible --version` n’est pas présente parmi les captures intégrées. Un contrôle local de syntaxe porte sur les blocs reproduits ici, sans accès aux VM et sans prouver l’identité avec des fichiers éventuellement modifiés sur le contrôleur.

## 2. Lire un playbook

Un fichier YAML décrit une liste de *plays*. Chaque play définit notamment ses cibles, ses privilèges et ses tâches. L'indentation matérialise les niveaux : les paramètres d'un module restent sous le nom de ce module. Dans ce kit, les tâches d'un play sont exécutées dans l'ordre où elles sont écrites. [Réf. 1](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html)

| Élément | Sens dans le kit |
|---|---|
| `---` | Début du document YAML |
| `- name:` | Nom lisible du play ou de la tâche ; ce n'est pas une commande |
| `hosts: postes` | Cible les machines du groupe d'inventaire `postes` |
| `become: true` | Active l'élévation de privilèges ; la méthode du kit est sudo, vers root par défaut |
| `serial: 1` | Traite les hôtes par lots d'un seul ; avec un seul client, l'effet n'est pas visible |
| `tasks:` | Liste des tâches du play |
| `ansible.builtin.…` | Nom complet d'un module fourni par ansible-core |
| `ansible.posix.…` | Module de la collection supplémentaire ansible.posix |
| `register:` | Enregistre le résultat d'une tâche dans une variable |
| `when:` | Condition qui détermine si une tâche doit s'exécuter |
| `changed_when: false` | Demande de ne pas déclarer de changement pour cette tâche ; ne désactive pas son exécution et ne masque pas ses erreurs |
| `{{ … }}` | Expression Jinja utilisée pour calculer une valeur ou lire une variable |
| `\| bool`, `\| b64decode` | Filtres appliqués à une valeur |
| `block: \|` | Texte multiligne conservant les retours à la ligne |
| `msg: >-` | Texte YAML replié pour former un message sans retour final |

Les mots-clés `hosts`, `become`, `serial`, `register`, `when` et `changed_when` sont décrits dans la référence Ansible. `-K` demande le mot de passe d'élévation ; il ne remplace pas la clé de connexion SSH. [Réf. 1](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html) [Réf. 2](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html)

### Collecte automatique des informations

Les plays ne désactivent pas la collecte des facts : la tâche implicite `Gathering Facts` recueille les caractéristiques de la cible avant les tâches écrites dans le fichier. Les informations sont ensuite accessibles dans `ansible_facts`, par exemple la distribution et sa version. Dans ce kit, `become: true` s'applique également à cette collecte : une erreur sudo peut donc apparaître dès cette première étape. [Réf. 1](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html)

## 3. Fichiers communs

### 3.1. `inventory.ini` : définir le client

```ini
# Laboratoire ECOCERT : deux VM dans le VLAN 53 Serveurs.
# Contrôleur : SRVANSIBLE — 172.16.53.10/24 (non ciblé par les playbooks).
# Client : CLIENTANSIBLE — 172.16.53.151/24.
# ansible_host utilise l'IP : aucune résolution DNS de CLIENTANSIBLE requise.
[postes]
CLIENTANSIBLE ansible_host=172.16.53.151

[postes:vars]
ansible_user=etudiant
ansible_ssh_private_key_file=~/.ssh/ecocert_ansible
```

- `[postes]` crée le groupe que les playbooks ciblent.
- `CLIENTANSIBLE` est le nom de la machine **dans l'inventaire**. Il ne renomme pas le système distant.
- `ansible_host=172.16.53.151` donne l'adresse utilisée pour joindre cette cible : la résolution du nom CLIENTANSIBLE n'est pas nécessaire pour cette connexion.
- `[postes:vars]` définit des variables communes aux membres du groupe.
- `ansible_user=etudiant` est le compte de connexion sur le client.
- `ansible_ssh_private_key_file` désigne la clé privée disponible sur SRVANSIBLE, dans le compte qui lance Ansible. Ce n'est pas un fichier à copier sur le client.

Le contrôleur n'est pas dans `[postes]` : les installations et changements de configuration ciblent le client, pas SRVANSIBLE. Les noms et variables de connexion correspondent au fonctionnement de l'inventaire Ansible. [Réf. 3](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)

### 3.2. `ansible.cfg` : fixer les options du projet

```ini
[defaults]
inventory = ./inventory.ini
host_key_checking = True
retry_files_enabled = False
interpreter_python = /usr/bin/python3

[privilege_escalation]
become = True
become_method = sudo
become_ask_pass = True
```

| Option | Explication |
|---|---|
| `inventory = ./inventory.ini` | Indique l'inventaire du projet ; exécuter les commandes depuis ce dossier |
| `host_key_checking = True` | Conserve la vérification de la clé d'hôte SSH ; comparer son empreinte avant d'accepter un nouvel hôte |
| `retry_files_enabled = False` | Désactive la production des anciens fichiers de relance `.retry` |
| `interpreter_python = /usr/bin/python3` | Fixe le chemin de Python sur les cibles |
| `become = True` | Active l'élévation par défaut dans ce projet ; elle est aussi explicite dans les plays |
| `become_method = sudo` | Utilise sudo, pas une connexion SSH directe comme root |
| `become_ask_pass = True` | Demande le mot de passe sudo au lancement |

La commande `ansible --version` permet de vérifier quel fichier de configuration est chargé. Les options d'élévation ne doivent pas conduire à stocker un mot de passe en clair dans l'inventaire. [Réf. 2](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html) [Réf. 4](https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html)

### 3.3. `group_vars/all.yml` : séparer les valeurs du code

```yaml
---
# Clé PUBLIQUE uniquement. La clé privée reste dans ~/.ssh sur SRVANSIBLE.
cle_publique: "{{ lookup('env', 'HOME') }}/.ssh/ecocert_ansible.pub"
applications:
  - htop

# Laisser false jusqu'à validation d'une NOUVELLE connexion par clé.
# Ce choix est un durcissement optionnel, pas une exigence explicite du sujet.
ssh_cles_uniquement: false
```

- `cle_publique` construit le chemin de la **clé publique sur le contrôleur**. `lookup('env', 'HOME')` lit le HOME du processus qui exécute Ansible. C'est pourquoi on lance les playbooks comme etudiant sur SRVANSIBLE, sans préfixer la commande entière par sudo.
- `applications` est une liste YAML. Ajouter un paquet à cette liste suffit pour qu'il soit pris en compte par 02.
- `ssh_cles_uniquement` pilote les deux expressions conditionnelles de 01. Avec `false`, l'authentification SSH par mot de passe reste permise ; avec `true`, le bloc impose la clé.

Ces valeurs n'effectuent rien seules : les tâches des playbooks doivent les utiliser. Le chargement des variables et l'utilisation de clés lues sur le contrôleur suivent les mécanismes d'inventaire et du module authorized_key. [Réf. 3](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html) [Réf. 5](https://docs.ansible.com/projects/ansible/latest/collections/ansible/posix/authorized_key_module.html)

## 4. `00-controles.yml` — vérifier le client et sudo

### Objectif

Vérifier que le client correspond à Debian 13, qu'Ansible peut y exécuter ses modules et que sudo permet d'obtenir l'identité root. Le code ne prévoit aucune modification de configuration.

### Code

```yaml
---
- name: Vérifier le poste pilote sans modifier sa configuration
  hosts: postes
  become: true
  tasks:
    - name: Vérifier Debian 13
      ansible.builtin.assert:
        that:
          - ansible_facts['distribution'] == 'Debian'
          - ansible_facts['distribution_major_version'] == '13'
        fail_msg: "Ce kit cible les clients Debian 13 du sujet."

    - name: Vérifier la connexion Ansible
      ansible.builtin.ping:

    - name: Vérifier les privilèges sudo
      ansible.builtin.command: id -u
      register: identite_root
      changed_when: false

    - name: Exiger les privilèges root
      ansible.builtin.assert:
        that: identite_root.stdout == '0'

    - name: Afficher la version du client
      ansible.builtin.debug:
        msg: "{{ inventory_hostname }} : {{ ansible_facts['distribution'] }} {{ ansible_facts['distribution_version'] }}"
```

### Explication des tâches

1. **Vérifier Debian 13.** Le module `assert` évalue deux expressions : la distribution doit être exactement `Debian` et sa version majeure doit être la chaîne `'13'`. Une révision comme 13.4 reste admise. Si une condition échoue, `fail_msg` explique pourquoi le déploiement ne correspond pas à cette ébauche.
2. **Vérifier la connexion Ansible.** `ansible.builtin.ping` vérifie l'exécution d'un module avec un Python utilisable et retourne normalement `pong`. Ce n'est **pas** un ping ICMP. La collecte des facts a déjà démontré une partie de cette capacité : cette tâche ajoute un contrôle lisible dans la recette. [Réf. 6](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/ping_module.html)
3. **Vérifier les privilèges sudo.** `command: id -u` exécute la commande sur le client avec les privilèges du play. `register: identite_root` conserve notamment sa sortie standard dans `identite_root.stdout`. `changed_when: false` convient car il s'agit d'une lecture d'identité, pas d'une modification. [Réf. 7](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html) [Réf. 1](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html)
4. **Exiger les privilèges root.** La seconde assertion exige la sortie `'0'`, UID de root. On vérifie donc le résultat de l'élévation, pas seulement l'absence apparente d'erreur.
5. **Afficher la version.** `debug` produit un message à partir du nom d'inventaire et des facts ; ce message est un résultat d'affichage, pas un changement de hostname.

### Exécution et résultat observé

```bash
ansible-playbook playbooks/00-controles.yml --limit CLIENTANSIBLE -K
```

La capture fournie indique `CLIENTANSIBLE : Debian 13.4` et `ok=6 changed=0 unreachable=0 failed=0`. Les six succès incluent la collecte implicite des facts.

**Limite :** ce playbook ne vérifie ni l'installation de Cinnamon, ni le VLAN réellement utilisé, ni une politique SSH imposant exclusivement la clé. Il ne doit pas être présenté comme une recette complète du sujet.

## 5. `01-ssh.yml` — gérer la clé et la configuration SSH

### Objectif

Maintenir l'autorisation de la clé du contrôleur et les paramètres SSH du client. Ce playbook suppose qu'un accès distant fonctionnel existe déjà : il ne peut pas amorcer ou réparer un client totalement inaccessible.

### Code

```yaml
---
- name: Gérer la clé et la configuration SSH
  hosts: postes
  become: true
  serial: 1
  tasks:
    - name: Installer le serveur SSH
      ansible.builtin.apt:
        name: openssh-server
        state: present
        update_cache: true
        cache_valid_time: 3600
        lock_timeout: 120

    - name: Assurer le fonctionnement de SSH
      ansible.builtin.service:
        name: ssh
        state: started
        enabled: true

    - name: Autoriser la clé du contrôleur sans supprimer les autres clés
      ansible.posix.authorized_key:
        user: etudiant
        key: "{{ lookup('file', cle_publique) }}"
        state: present
        exclusive: false

    # Au début du fichier : avant Include et tout bloc Match.
    # La première valeur rencontrée compte pour ces directives SSH.
    - name: Gérer les paramètres globaux et valider avant écriture
      ansible.builtin.blockinfile:
        path: /etc/ssh/sshd_config
        insertbefore: BOF
        marker: '# {mark} ANSIBLE ECOCERT'
        backup: true
        validate: '/usr/sbin/sshd -t -f %s'
        block: |
          PubkeyAuthentication yes
          PermitRootLogin no
          PasswordAuthentication {{ 'no' if ssh_cles_uniquement | bool else 'yes' }}
          KbdInteractiveAuthentication no
          AuthenticationMethods {{ 'publickey' if ssh_cles_uniquement | bool else 'any' }}
      notify: Recharger SSH

    - name: Appliquer le rechargement immédiatement
      ansible.builtin.meta: flush_handlers

    - name: Lire la configuration globale effective
      ansible.builtin.command: /usr/sbin/sshd -T
      register: ssh_effectif
      changed_when: false
      check_mode: false

    - name: Vérifier l'activation globale des clés
      ansible.builtin.assert:
        that: "'pubkeyauthentication yes' in ssh_effectif.stdout_lines"
        fail_msg: "Vérifier les directives Include/Match et garder la console ouverte."

    # Vérification réelle supplémentaire à faire depuis le contrôleur :
    # ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no ...
    # Si le fichier contient des Match, tester aussi sshd -T -C user=...,addr=...,host=...
  handlers:
    - name: Recharger SSH
      ansible.builtin.service:
        name: ssh
        state: reloaded
```

### 5.1. Installer le serveur SSH et assurer son fonctionnement

`apt` demande l'état `present` pour `openssh-server` : le paquet est installé s'il manque, mais sa présence ne demande pas automatiquement la dernière version disponible. `service` demande que `ssh` soit démarré (`state: started`) et activé au démarrage (`enabled: true`). [Réf. 8](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/apt_module.html) [Réf. 9](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/service_module.html)

Les options APT réutilisées dans plusieurs fichiers signifient :

| Option | Sens |
|---|---|
| `update_cache: true` | Demande l'actualisation des index de paquets |
| `cache_valid_time: 3600` | Permet de conserver un cache encore valide pendant 3 600 secondes, soit une heure |
| `lock_timeout: 120` | Attend jusqu'à 120 secondes pour acquérir le verrou APT ; ce n'est pas une durée maximale de téléchargement ou d'installation |

Ces paramètres sont ceux du module APT. [Réf. 8](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/apt_module.html)

### 5.2. Ajouter la clé sans supprimer les autres

`ansible.posix.authorized_key` gère la clé autorisée du compte distant `etudiant`.

- `lookup('file', cle_publique)` lit le fichier public **sur SRVANSIBLE**, puis fournit son contenu au module.
- `state: present` exige la présence de cette clé dans les clés autorisées du compte.
- `exclusive: false` conserve les autres clés présentes.

La collection `ansible.posix` doit être disponible sur le contrôleur. La clé privée, elle, ne quitte pas SRVANSIBLE. [Réf. 5](https://docs.ansible.com/projects/ansible/latest/collections/ansible/posix/authorized_key_module.html)

### 5.3. Gérer un bloc de configuration

`blockinfile` maintient un bloc délimité dans `/etc/ssh/sshd_config` :

| Paramètre | Rôle |
|---|---|
| `path` | Fichier distant modifié |
| `insertbefore: BOF` | Lors de la première insertion, place le bloc au début du fichier |
| `marker: '# {mark} ANSIBLE ECOCERT'` | Produit les repères BEGIN et END permettant de retrouver le bloc |
| `backup: true` | Crée une sauvegarde horodatée du fichier avant modification |
| `validate: '/usr/sbin/sshd -t -f %s'` | Teste une version temporaire du fichier avant son installation à la destination |

`%s` est remplacé par le chemin du fichier temporaire. Si la validation échoue, le nouveau contenu n'est pas installé par cette tâche. Si le bloc existe déjà, Ansible le retrouve par ses marqueurs : `insertbefore: BOF` ne doit pas être interprété comme une garantie de déplacement automatique d'un bloc préexistant. [Réf. 10](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/blockinfile_module.html)

Le placement initial en tête vise à faire lire ces valeurs avant les autres directives globales : pour les paramètres concernés, OpenSSH retient généralement la première valeur obtenue. Des blocs conditionnels `Match` peuvent toutefois déterminer des valeurs propres à une connexion. [Réf. 11](https://man.openbsd.org/sshd_config)

### 5.4. Comprendre les directives SSH

| Directive | Effet attendu |
|---|---|
| `PubkeyAuthentication yes` | Autorise l'authentification par clé publique |
| `PermitRootLogin no` | Interdit une connexion SSH directe au compte root ; sudo depuis etudiant reste distinct |
| `PasswordAuthentication …` | Autorise ou interdit la méthode SSH par mot de passe selon la variable |
| `KbdInteractiveAuthentication no` | Désactive la méthode interactive clavier |
| `AuthenticationMethods …` | Définit les méthodes suffisantes/requises pour réussir l'authentification |

Avec `ssh_cles_uniquement: false`, les expressions Jinja produisent :

```text
PasswordAuthentication yes
AuthenticationMethods any
```

Cela **n'exige pas simultanément** une clé et un mot de passe : une méthode admise peut suffire. Avec `true`, elles produisent :

```text
PasswordAuthentication no
AuthenticationMethods publickey
```

Dans ce second cas, le bloc exige la clé publique. Tester une nouvelle connexion avant et après ce durcissement, console disponible ; ne pas l'activer uniquement parce que la syntaxe est valide. [Réf. 11](https://man.openbsd.org/sshd_config)

### 5.5. Recharger et contrôler

`notify: Recharger SSH` programme le handler uniquement si la tâche du bloc rapporte un changement. `meta: flush_handlers` exécute les handlers déjà notifiés à cet endroit, avant la lecture de la configuration effective. Le handler utilise `state: reloaded`, pas un redémarrage systématique du service. [Réf. 12](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)

La commande `sshd -T` affiche les paramètres effectifs globaux et contrôle la configuration. Le résultat est stocké dans `ssh_effectif` ; l'assertion exige la présence de la ligne `pubkeyauthentication yes`. `changed_when: false` classe cette lecture comme inchangée. `check_mode: false` force cette lecture même lors d'un lancement avec `--check` : cela lit la configuration réelle, pas un fichier hypothétique uniquement simulé. [Réf. 13](https://man.openbsd.org/sshd) [Réf. 14](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)

### Exécution, preuves et limites

```bash
ansible-playbook playbooks/01-ssh.yml --limit CLIENTANSIBLE -K --diff
```

La capture montre deux changements : écriture du bloc et rechargement SSH. La clé était déjà présente. L’assertion finale est passée. La capture de connexion manuelle est antérieure au déploiement : le test ci-dessous reste à refaire après celui-ci.

Cette réussite ne prouve pas à elle seule une nouvelle authentification. Sur SRVANSIBLE :

```bash
ssh -i ~/.ssh/ecocert_ansible -o IdentitiesOnly=yes \
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
  etudiant@172.16.53.151
```

Si des `Match` existent, examiner sur le client une configuration contextualisée, par exemple :

```bash
sudo /usr/sbin/sshd -T -C user=etudiant,addr=172.16.53.10,host=SRVANSIBLE
```

Le nom et l'adresse doivent représenter la connexion réelle, notamment en présence de règles Match Host ou de traduction d'adresses. `-t`/`-T` ne remplacent pas le test d'authentification. [Réf. 13](https://man.openbsd.org/sshd)

**Retour arrière :** depuis la console du client, restaurer la sauvegarde SSH appropriée, exécuter `sshd -t`, puis recharger le service seulement si le contrôle réussit. Le playbook ne prévoit pas de restauration automatique après un échec ultérieur.

## 6. `02-applications.yml` — installer une liste de paquets

### Code

```yaml
---
- name: Installer les applications de la salle
  hosts: postes
  become: true
  tasks:
    - name: Installer la liste de paquets demandée
      ansible.builtin.apt:
        name: "{{ applications }}"
        state: present
        update_cache: true
        cache_valid_time: 3600
        lock_timeout: 120
```

### Explication

Le module `apt` reçoit directement la liste `applications` chargée depuis `group_vars/all.yml`. Avec la valeur du kit, il demande l'installation de `htop`. Une liste de noms évite d'écrire une tâche distincte par paquet. `state: present` exige la présence du paquet sans imposer une mise à jour à chaque passage ; les autres paramètres APT sont ceux expliqués en 5.1. [Réf. 8](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/apt_module.html)

Pour ajouter des applications, modifier les données plutôt que le playbook :

```yaml
applications:
  - htop
  - tree
```

Les noms doivent correspondre à des paquets disponibles dans les dépôts du client. Retirer un nom de la liste **ne désinstalle pas** le paquet : le code ne contient aucune demande `state: absent`.

### Exécution et contrôle

```bash
ansible-playbook playbooks/02-applications.yml --limit CLIENTANSIBLE -K --diff
```

Sur le client, pour la configuration initiale :

```bash
dpkg-query -W htop
```

Au deuxième passage, un paquet déjà présent n'est pas à réinstaller. Un rafraîchissement de cache peut néanmoins expliquer un changement. La capture de 02 confirme `ok=2 changed=1 unreachable=0 failed=0`, avec installation de htop. La sortie textuelle du compte rendu rapporte `htop 3.4.1-5`.

## 7. `03-mises-a-jour.yml` — mettre à jour à la demande

### Code

```yaml
---
- name: Mettre à jour les postes sans redémarrage imposé
  hosts: postes
  become: true
  serial: 1
  tasks:
    - name: Rafraîchir les index et appliquer les mises à jour
      ansible.builtin.apt:
        update_cache: true
        upgrade: safe
        force_apt_get: true
        lock_timeout: 120

    - name: Rechercher l'indicateur de redémarrage s'il existe
      ansible.builtin.stat:
        path: /var/run/reboot-required
      register: redemarrage

    - name: Signaler un redémarrage demandé par les paquets
      ansible.builtin.debug:
        msg: >-
          {{ 'Un paquet signale un redémarrage à prévoir.' if redemarrage.stat.exists
          else "Pas d'indicateur reboot-required : cela ne garantit pas qu'aucun redémarrage ne soit utile." }}
```

### Explication des tâches

1. **Mise à jour APT.** `update_cache: true` actualise les index avant la mise à niveau. `upgrade: safe` demande le mode de mise à jour « safe » ; `force_apt_get: true` impose l'usage d'apt-get plutôt qu'aptitude. Ce playbook n'utilise pas le mode `dist` et ne demande pas d'autoremove. Le mot « safe » désigne un mode du module, pas une garantie d'absence d'incident. [Réf. 8](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/apt_module.html)
2. **Lecture d'un indicateur.** `stat` consulte le chemin `/var/run/reboot-required`. Le résultat enregistré dans `redemarrage` expose le booléen `redemarrage.stat.exists`. [Réf. 15](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/stat_module.html)
3. **Affichage conditionnel.** L'expression Jinja choisit le message selon l'existence de cet indicateur. Le code ne contient ni module `reboot`, ni commande de redémarrage.

### Exécution et limites

```bash
ansible-playbook playbooks/03-mises-a-jour.yml --limit CLIENTANSIBLE -K
```

Ce playbook effectue la mise à jour **lorsqu'on le lance**. Il ne crée pas de calendrier. Des services peuvent être redémarrés par les paquets eux-mêmes ; prendre un instantané et choisir une période de maintenance. Le test d'un seul fichier de signalement ne permet pas de conclure, en son absence, qu'aucun redémarrage n'est utile.

`serial: 1` limite le lot à un poste, mais ne transforme pas une mise à jour en transaction avec retour arrière. Le kit ne prévoit pas de rétrogradation de masse ; utiliser l'instantané du pilote si un retour arrière s'impose.

## 8. `04-mots-de-passe.yml` — contrôler les futurs mots de passe locaux

### Objectif et précaution

Activer un contrôle de qualité lors des changements de mots de passe via PAM. PAM organise les modules utilisés pour l'authentification et les changements de secrets ; modifier cette pile demande un instantané et une console root conservée ouverte. Le playbook ne définit aucun mot de passe et ne tente pas de lire les secrets existants.

### Code

```yaml
---
- name: Appliquer une politique aux changements de mots de passe locaux
  hosts: postes
  become: true
  serial: 1
  tasks:
    # Sauvegarde avant l'installation, qui peut elle-même modifier PAM.
    - name: Sauvegarder la pile PAM une seule fois pour ce TP
      ansible.builtin.command:
        argv: [cp, -a, /etc/pam.d, /root/ecocert-pam-avant-tp]
        creates: /root/ecocert-pam-avant-tp

    - name: Installer le contrôle de qualité et le dictionnaire
      ansible.builtin.apt:
        name:
          - libpam-pwquality
          - cracklib-runtime
          - wamerican
        state: present
        update_cache: true
        cache_valid_time: 3600
        lock_timeout: 120

    - name: Lire la pile des changements de mots de passe
      ansible.builtin.slurp:
        src: /etc/pam.d/common-password
      register: pam_initial

    # Le profil est normalement activé à l'installation. Sans --force :
    # ne pas écraser une pile PAM déjà personnalisée.
    - name: Activer le profil Debian uniquement s'il manque
      ansible.builtin.command: pam-auth-update --enable pwquality
      environment:
        DEBIAN_FRONTEND: noninteractive
      when: >-
        (pam_initial.content | b64decode | regex_search('(?m)^password\s+.*pam_pwquality\.so')) is none

    - name: Relire PAM après activation éventuelle
      ansible.builtin.slurp:
        src: /etc/pam.d/common-password
      register: pam_active

    - name: Vérifier l'ordre et l'unicité des modules avant modification
      ansible.builtin.assert:
        that:
          - >-
            (pam_active.content | b64decode | regex_findall('(?m)^password\s+.*pam_pwquality\.so')) | length == 1
          - >-
            (pam_active.content | b64decode | regex_search('(?s)password[^\n]*pam_pwquality\.so.*password[^\n]*pam_unix\.so[^\n]*use_authtok')) is not none
        fail_msg: "Pile PAM personnalisée ou profil inactif : inspecter common-password, ne pas utiliser --force à l'aveugle."

    # Les arguments du module priment sur pwquality.conf et conf.d.
    # Pas de remplacement intégral de common-password ni de modification de pam_unix.
    - name: Définir les règles explicites sur le module pwquality
      ansible.builtin.lineinfile:
        path: /etc/pam.d/common-password
        regexp: '^password\s+.*pam_pwquality\.so.*$'
        line: 'password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=0 minclass=3 dictcheck=1 usercheck=1 enforcing=1 enforce_for_root local_users_only'
        backup: true

    - name: Rappeler le périmètre de la politique
      ansible.builtin.debug:
        msg: >-
          Tester avec passwd sur un compte jetable, console root ouverte.
          Les mots de passe existants ne sont ni analysés ni renouvelés.
          Aucun mot de passe n'est défini par ce playbook.
```

### 8.1. Sauvegarder avant l'installation

Le module `command` reçoit une liste `argv` équivalente à :

```bash
cp -a /etc/pam.d /root/ecocert-pam-avant-tp
```

`argv` passe les arguments sans recourir à un shell. `creates` évite de relancer la copie si le chemin de sauvegarde existe déjà. Il s'agit donc d'une sauvegarde initiale pour le TP, **pas d'un historique renouvelé à chaque exécution**. Le module ne vérifie pas ici la complétude d'une sauvegarde préexistante. [Réf. 7](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html)

### 8.2. Installer les composants

La tâche APT demande `libpam-pwquality`, `cracklib-runtime` et `wamerican`. L'intention est de disposer du module de contrôle, des outils associés et d'un dictionnaire. `wamerican` est un dictionnaire anglais : sa présence ne suffit pas à démontrer une protection contre tous les mots faibles français. Les tests de qualité et leurs paramètres sont ceux du module `pam_pwquality`. [Réf. 16](https://manpages.debian.org/trixie/libpam-pwquality/pam_pwquality.8.en.html)

### 8.3. Lire puis activer le profil si nécessaire

`slurp` lit `/etc/pam.d/common-password` sur le client et ramène son contenu dans `pam_initial.content`, encodé en Base64. Le filtre `b64decode` reconstruit le texte pour les tests. **Base64 n'est pas un chiffrement.** Il ne s'agit pas ici de transférer `/etc/shadow` : le fichier lu décrit la pile des changements de mots de passe. [Réf. 17](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/slurp_module.html)

La condition recherche une ligne commençant par `password`, contenant `pam_pwquality.so`. Si elle n'existe pas (`is none`), la commande suivante est exécutée :

```bash
pam-auth-update --enable pwquality
```

`DEBIAN_FRONTEND: noninteractive` est une variable d'environnement fournie à cette tâche. Elle n'inscrit pas de réglage permanent dans le shell utilisateur. Le code n'emploie pas `--force` : pam-auth-update doit respecter les configurations locales personnalisées. Une pile qu'il refuse de gérer ne doit pas être écrasée à l'aveugle. [Réf. 1](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html) [Réf. 18](https://manpages.debian.org/trixie/libpam-runtime/pam-auth-update.8.en.html)

### 8.4. Comprendre les expressions régulières de contrôle

Après une seconde lecture dans `pam_active`, deux assertions inspectent le texte :

| Élément du motif | Signification |
|---|---|
| `(?m)` | Rend `^` applicable au début de chaque ligne |
| `^password` | Cherche une ligne de type password, non commentée, commençant exactement ainsi |
| `\s+` | Un ou plusieurs caractères d'espacement |
| `.*` | Une suite quelconque de caractères, selon les options du motif |
| `pam_pwquality\.so` | Nom du module, avec un point littéral |
| `regex_findall(...) \| length == 1` | Exige une seule correspondance du premier motif |
| `(?s)` | Permet au point de couvrir aussi les retours à la ligne |
| `[^\n]*` | Reste sur la même ligne jusqu'au prochain retour |
| `is not none` | Exige qu'une correspondance ait été trouvée |

Le premier test exige une seule ligne reconnue de pwquality. Le second cherche ensuite une ligne `pam_unix.so` comportant `use_authtok`, après celle de pwquality. L'intention est de contrôler la qualité avant l'enregistrement et de transmettre le nouveau secret au module suivant, au lieu de lui demander un autre mot de passe. [Réf. 16](https://manpages.debian.org/trixie/libpam-pwquality/pam_pwquality.8.en.html)

**Limite de ces assertions :** ce sont des recherches textuelles adaptées à une pile Debian simple, pas un analyseur complet de PAM. Elles peuvent refuser une présentation personnalisée pourtant valide et ne démontrent pas la correction de tous les branchements d'une pile complexe. Si elles échouent, inspecter le fichier plutôt que retirer le contrôle.

### 8.5. Modifier une ligne, pas toute la pile

`lineinfile` remplace la ligne reconnue par `regexp` avec la valeur `line`. `backup: true` conserve une copie horodatée de `common-password`. Le module remplacerait normalement la dernière ligne correspondante ; l'assertion précédente vise justement à refuser les doublons. Le motif reconnaît aussi la ligne après remplacement, ce qui permet une nouvelle exécution sans ajouter de ligne supplémentaire. [Réf. 19](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/lineinfile_module.html)

Le début de la ligne a le sens suivant :

```text
password requisite pam_pwquality.so
```

- `password` : pile de changement de mot de passe, pas pile d'ouverture de session.
- `requisite` : un échec du contrôle est bloquant dans cette pile.
- `pam_pwquality.so` : module qui applique les vérifications de qualité.

Les arguments du module prennent le pas sur les paramètres de ses fichiers de configuration ; ils sont donc explicités sur cette ligne. [Réf. 16](https://manpages.debian.org/trixie/libpam-pwquality/pam_pwquality.8.en.html)

| Argument | Effet de la valeur retenue |
|---|---|
| `retry=3` | Autorise jusqu'à trois propositions lors de la demande d'un nouveau mot de passe ; ce n'est pas une limite des tentatives de connexion |
| `minlen=14` | Définit la longueur minimale retenue, sans bonus positifs dans les crédits choisis ici |
| `dcredit=-1` | Exige au moins un chiffre |
| `ucredit=-1` | Exige au moins une majuscule |
| `lcredit=-1` | Exige au moins une minuscule |
| `ocredit=0` | Ne donne pas de crédit supplémentaire aux autres caractères et n'en impose pas ; ils restent autorisés |
| `minclass=3` | Exige au moins trois classes ; redondant ici avec les trois exigences précédentes, mais explicite l'intention |
| `dictcheck=1` | Active le contrôle de dictionnaire |
| `usercheck=1` | Active le contrôle fondé sur le nom utilisateur, avec les limites documentées du module |
| `enforcing=1` | Rend les contrôles bloquants plutôt que de simples avertissements |
| `enforce_for_root` | Rend le refus applicable aussi lorsque root utilise ce mécanisme de changement |
| `local_users_only` | Limite les vérifications de qualité aux comptes présents dans `/etc/passwd` |

Les paramètres ne garantissent pas une conformité globale à eux seuls. La CNIL présente une politique à 14 caractères avec majuscules, minuscules et chiffres comme un exemple ; l'ANSSI demande d'adapter les moyens d'authentification au risque et au contexte. [Réf. 16](https://manpages.debian.org/trixie/libpam-pwquality/pam_pwquality.8.en.html) [Réf. 20](https://www.cnil.fr/fr/mots-de-passe-recommandations-pour-maitriser-sa-securite) [Réf. 21](https://messervices.cyber.gouv.fr/guides/recommandations-relatives-lauthentification-multifacteur-et-aux-mots-de-passe)

### Exécution et recette

```bash
ansible-playbook playbooks/04-mots-de-passe.yml --limit CLIENTANSIBLE -K --diff
```

Sur le client, utiliser un compte temporaire pour ne pas toucher au compte d'administration :

```bash
sudo adduser --disabled-password --gecos '' testqualite
sudo passwd testqualite
```

Tester le refus effectif d'un mot de passe trop court puis l'acceptation d'un conforme, sans publier ces secrets. Vérifier aussi le changement avec `passwd` depuis une session du compte de test, puis supprimer celui-ci :

```bash
sudo deluser --remove-home testqualite
```

**Limites :** les mots de passe existants ne sont ni examinés ni renouvelés. Le playbook ne règle pas l'historique, la périodicité de renouvellement, le verrouillage après échecs de connexion ou l'authentification multifacteur. Un administrateur capable de modifier PAM ou les bases de comptes peut contourner cette politique : `enforce_for_root` n'est pas une frontière de sécurité contre root. Certaines vérifications de comparaison à l'ancien secret ne s'appliquent pas lorsque root le réinitialise. [Réf. 16](https://manpages.debian.org/trixie/libpam-pwquality/pam_pwquality.8.en.html)

Contrairement au bloc SSH, la tâche PAM ne possède pas de validation externe `validate` avant écriture, et aucune restauration automatique n'est prévue. Conserver la console et l'instantané jusqu'à la réussite des tests. Une sauvegarde existe, mais il faut choisir et appliquer soi-même le retour arrière approprié.

## 9. `05-maj-automatiques.yml` — activer la périodicité sur les clients

### Code

```yaml
---
# À lancer séparément, après contrôle des origines APT sur le poste pilote.
- name: Activer les mises à jour périodiques sur les clients
  hosts: postes
  become: true
  serial: 1
  tasks:
    - name: Installer unattended-upgrades
      ansible.builtin.apt:
        name: unattended-upgrades
        state: present
        update_cache: true
        cache_valid_time: 3600
        lock_timeout: 120

    - name: Configurer la périodicité et interdire les redémarrages automatiques
      ansible.builtin.copy:
        dest: /etc/apt/apt.conf.d/99ecocert-periodic
        owner: root
        group: root
        mode: '0644'
        backup: true
        content: |
          // Origines autorisées : conserver la politique Debian, à vérifier.
          APT::Periodic::Enable "1";
          APT::Periodic::Update-Package-Lists "1";
          APT::Periodic::Unattended-Upgrade "1";
          Unattended-Upgrade::Automatic-Reboot "false";

    - name: Activer les minuteurs APT existants
      ansible.builtin.systemd_service:
        name: '{{ item }}'
        enabled: true
        state: started
      loop:
        - apt-daily.timer
        - apt-daily-upgrade.timer
```

### 9.1. Installer le moteur de mises à jour

La tâche APT installe `unattended-upgrades` sur les cibles. C'est le client qui effectuera ensuite ses mises à jour périodiques ; le contrôleur n'a pas besoin de conserver un mot de passe sudo pour une exécution nocturne d'Ansible. [Réf. 22](https://wiki.debian.org/PeriodicUpdates)

### 9.2. Écrire un fragment de configuration APT

`copy` écrit directement le contenu YAML multiligne dans `/etc/apt/apt.conf.d/99ecocert-periodic`.

- `owner: root` et `group: root` fixent le propriétaire et le groupe.
- `mode: '0644'` donne lecture/écriture au propriétaire et lecture aux autres. Les guillemets évitent une interprétation numérique inattendue des permissions.
- `backup: true` sauvegarde un fichier existant avant son remplacement.
- `content: |` contient le texte APT à installer ; ce n'est pas du code shell.

`copy` remet le contenu demandé si le fichier diffère ; il ne réécrit pas systématiquement un fichier déjà conforme. [Réf. 23](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/copy_module.html)

| Directive APT | Intention de la valeur |
|---|---|
| `APT::Periodic::Enable "1";` | Active le mécanisme périodique |
| `APT::Periodic::Update-Package-Lists "1";` | Demande l'actualisation périodique des index, avec un intervalle d'un jour |
| `APT::Periodic::Unattended-Upgrade "1";` | Demande l'exécution périodique d'unattended-upgrades, avec un intervalle d'un jour |
| `Unattended-Upgrade::Automatic-Reboot "false";` | Interdit au mécanisme unattended-upgrades de redémarrer automatiquement la machine |

Ces intervalles ne définissent pas une heure exacte : les unités et timers APT déterminent les déclenchements. Le fragment ne choisit aucune nouvelle origine de paquets. La sélection repose sur la politique unattended-upgrades déjà présente, à inspecter avant activation. [Réf. 22](https://wiki.debian.org/PeriodicUpdates)

Le préfixe `99` place le fichier tard dans l'ordre de lecture des fragments APT, mais ne garantit pas qu'aucune autre configuration ne puisse prendre le dessus. Les fragments sont lus dans l'ordre alphanumérique ; le fichier principal et les options de commande peuvent aussi intervenir. Contrôler la configuration résultante avec `apt-config dump`. [Réf. 24](https://manpages.debian.org/trixie/apt/apt.conf.5.en.html)

### 9.3. Activer les timers existants

La boucle passe successivement les deux noms dans la variable `item` :

```text
apt-daily.timer
apt-daily-upgrade.timer
```

`systemd_service` cible chaque unité : `enabled: true` l'active au démarrage et `state: started` la rend active maintenant. L'état `started` ne redémarre pas une unité déjà active. Ces tâches ne créent pas de nouvelles unités et ne changent pas leur calendrier. [Réf. 25](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/systemd_service_module.html)

### Préparation, exécution et contrôles

Avant activation, sur le client :

```bash
sudo apt install unattended-upgrades
sudo apt-config dump | grep -E 'Origins-Pattern|Allowed-Origins|APT::Periodic|Automatic-Reboot'
sudo unattended-upgrade --dry-run --debug
```

Lire les origines autorisées et les paquets candidats. Sur une installation Debian standard, la configuration vise typiquement la sécurité ; une VM déjà modifiée peut avoir une autre politique. Ce playbook n'est donc pas une preuve que **toutes** les mises à jour deviennent périodiques. [Réf. 22](https://wiki.debian.org/PeriodicUpdates)

Après cette vérification, depuis SRVANSIBLE :

```bash
ansible-playbook playbooks/05-maj-automatiques.yml --limit CLIENTANSIBLE -K --diff
```

Puis sur le client :

```bash
systemctl list-timers 'apt-daily*'
sudo apt-config dump | grep -E 'APT::Periodic|Automatic-Reboot'
sudo unattended-upgrade --dry-run --debug
sudo journalctl -u apt-daily-upgrade.service --no-pager -n 50
```

L'essai à blanc montre la sélection prévue, pas la réussite d'un futur déclenchement. Conserver ensuite un journal d'exécution réel. Un timer n'est pas une garantie que la VM sera allumée et joignable au moment souhaité.

**Différence à retenir :** 03 applique des mises à jour à la demande via Ansible ; 05 installe la configuration qui permet au client de traiter périodiquement les origines autorisées, même sans nouvelle commande Ansible.

## 10. `site.yml` — regrouper certains plays

### Code

```yaml
---
# Pas de mise à jour générale dans ce scénario, pour éviter de la lancer par accident.
- import_playbook: playbooks/00-controles.yml
- import_playbook: playbooks/01-ssh.yml
- import_playbook: playbooks/02-applications.yml
- import_playbook: playbooks/04-mots-de-passe.yml
```

Chaque `import_playbook` importe un autre playbook dans l'ordre du fichier. Le regroupement lance donc 00, puis 01, puis 02, puis 04, sous réserve des échecs rencontrés. Il n'importe ni 03 ni 05 : les mises à jour générales et leur périodicité restent des actions séparées. [Réf. 26](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse.html)

```bash
ansible-playbook site.yml --limit CLIENTANSIBLE -K --diff
```

Pour la première recette, privilégier les lancements individuels afin d'identifier précisément le comportement et les changements de chaque fichier. Le regroupement n'ajoute ni sauvegarde globale ni retour arrière transactionnel.

## 11. Lire les résultats et vérifier l'idempotence

| Résultat | Lecture |
|---|---|
| `ok` | Tâche réussie ; le compteur récapitulatif inclut aussi les tâches réussies qui ont changé quelque chose |
| `changed` | Parmi les tâches réussies, celles qui ont déclaré un changement |
| `unreachable` | Problème d'accès ou de transport vers l'hôte |
| `failed` | Tâche ayant échoué |
| `skipped` | Tâche non exécutée, par exemple en raison d'une condition |

L'idempotence consiste ici à redemander le même état sans réappliquer inutilement les changements déjà satisfaits. Elle ne signifie pas qu'une seconde exécution entière affichera toujours `changed=0` : un index APT peut être rafraîchi, de nouvelles versions peuvent apparaître et une commande peut déclarer un changement par défaut. Les modules d'état et `changed_when` déterminent les statuts rapportés. [Réf. 1](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html) [Réf. 8](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/apt_module.html)

Pour la recette, relancer séparément 01, 02 et 04, puis expliquer les changements restants. En particulier, `pam-auth-update` n'est lancé que si le contrôle textuel considère le module absent ; ce n'est pas une opération effectuée à chaque passage.

### Syntaxe, simulation et tests réels

```bash
# Vérification de syntaxe, pas de déploiement :
ansible-playbook playbooks/01-ssh.yml --syntax-check

# Aperçu, avec les limites du mode check :
ansible-playbook playbooks/01-ssh.yml --limit CLIENTANSIBLE -K --check --diff
```

`--syntax-check` ne démontre ni la connectivité, ni le succès sudo, ni la validité fonctionnelle de la configuration distante. `--check` est une simulation dépendant des modules et des résultats disponibles. Les commandes sans `creates`/`removes` sont généralement ignorées en mode check ; des assertions fondées sur leurs résultats peuvent donc ne pas fonctionner comme en exécution réelle. La lecture `sshd -T` de 01 est explicitement forcée par `check_mode: false`. [Réf. 7](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html) [Réf. 14](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)

Ne pas afficher de secrets dans les captures ou les journaux. Le kit ne stocke pas de mot de passe utilisateur dans ses variables ; la clé privée reste sur le contrôleur.

## 12. Synthèse pour le compte rendu

| Fichier | Ce qu'il réalise | Preuve à produire |
|---|---|---|
| 00 | Contrôle Debian, exécution Ansible et sudo | Sortie réussie avec vérification de l'UID root |
| 01 | Maintient clé et configuration SSH | Diff, rechargement, configuration effective et nouvelle connexion par clé |
| 02 | Installe les paquets demandés | Sortie Ansible et paquet présent sur le client |
| 03 | Met à jour à la demande | Sortie de l'opération et contrôle du poste après mise à jour |
| 04 | Contrôle la qualité lors des futurs changements de mots de passe locaux | Refus d'un secret faible et acceptation d'un conforme, sans les exposer |
| 05 | Active la mise à jour périodique selon les origines autorisées | Configuration effective, timers, essai à blanc puis journal réel |
| site.yml | Regroupe 00, 01, 02 et 04 | Exécution complète, après validation individuelle |

Les codes ci-dessus sont ceux de l'archive préparée ; si les fichiers du serveur ont été modifiés depuis leur transfert, comparer leur contenu avant de présenter cette documentation comme la description exacte de la version exécutée.

## Références et versions

Les liens numérotés au fil du texte renvoient aux documentations officielles consultées. Les pages Ansible `latest` peuvent décrire une version plus récente que **2.19.11**, utilisée sur SRVANSIBLE ; les paramètres reproduits restent ceux des fichiers du kit, sans ajout des nouveautés documentaires. Les pages PAM et APT citées sont celles de Debian **trixie**. Les manuels OpenSSH en ligne cités décrivent OpenBSD-current : vérifier au besoin les options et défauts locaux avec `man sshd` et `man sshd_config`.

Les exigences métier et le plan réseau proviennent du sujet SP3 et des trois PDF GP3 joints par Ewen. Les résultats d'exécution rapportés en section 1 proviennent des sorties et captures intégrées au compte rendu de la séance.
