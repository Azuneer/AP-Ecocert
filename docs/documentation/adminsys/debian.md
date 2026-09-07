# Debian

Documentation relative à l'administration de **Debian** dans le contexte Ecocert.

## Services déployés sous Debian

- **DHCP** : distribution des paramètres réseau à tous les sous-réseaux
- **NAS** : serveur de sauvegardes (RAID 5)
- **Contrôleur WiFi Unifi OS** : gestion des bornes Ubiquiti

## Serveurs concernés

| Serveur | IP | Service |
|---------|-----|---------|
| DHCPECOCERT | 172.16.5X.2 | DHCP |
| NASECOCERT | 172.16.5X.20 | Sauvegardes |
| WIFIECOCERT | 172.16.5X.30 | Contrôleur WiFi |

## Commandes utiles

```shell
# Mise à jour
sudo apt update && sudo apt upgrade -y

# Installation de paquets
sudo apt install <paquet>

# Vérification des services
sudo systemctl status <service>
sudo journalctl -u <service> -f
```

## Voir aussi

- [Windows Server](windows-server.md)
- [DHCP](../services/dhcp.md)