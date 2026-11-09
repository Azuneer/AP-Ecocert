# Missions

Vue d'ensemble des missions du projet AP-ECOCERT et des situations d’exploration.

## Planning

| Mission | Description | Livrable |
|---------|-------------|----------|
| **Mission 1** | Plan d'adressage VLSM | Nouveau plan d'adressage validé |
| **Mission 2** | AD + DHCP | Contrôleur de domaine + serveur DHCP opérationnels |
| **Mission 3** | GLPI + NAS | Serveur de tickets + sauvegardes en RAID 5 |
| **Mission 4** | Architecture réseau | Maquette Packet Tracer + mise en place physique |

---

<div class="grid cards" markdown>

- :material-map-marker-distance:{ .lg .middle } __Mission 1__

    ---

    Segmenter le réseau en VLSM avec une marge de 20%.

    [:octicons-arrow-right-24: Détail](mission1.md)

- :material-server:{ .lg .middle } __Mission 2__

    ---

    AD (Windows 2019) + DHCP (Debian).

    [:octicons-arrow-right-24: Détail](mission2.md)

- :material-clipboard-check-outline:{ .lg .middle } __Mission 3__

    ---

    GLPI (gestion d'incidents) + NAS (RAID 5).

    [:octicons-arrow-right-24: Détail](mission3.md)

- :material-router-network:{ .lg .middle } __Mission 4__

    ---

    Cisco 9200/2960 + Stormshield SN210 + WiFi Ubiquiti.

    [:octicons-arrow-right-24: Détail](mission4.md)  
    [Recette réseau](mission4-recette.md) · [Recette Wi-Fi — en cours](mission4-recette-wifi.md)


- :material-file-document-multiple:{ .lg .middle } __Toutes les productions du vault__

    ---

    Fiches, annexes, documents techniques et brouillons en cours.

    [Consulter les productions](../ressources/productions.md)

- :material-cog-sync:{ .lg .middle } __SP3 — Automatisation avec Ansible__

    ---

    Configuration des postes Debian, SSH, applications, mises à jour et politique de mots de passe.

    [Compte rendu et recette](sp3-ansible.md) · [Fonctionnement](../documentation/adminsys/ansible.md) · [Playbooks expliqués](../documentation/adminsys/ansible-playbooks.md)

</div>