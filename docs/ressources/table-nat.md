# Table NAT - Ecocert GP3

> :bust_in_silhouette: **Fiche rédigée par** : GADONNAUD Ewen  
> :mortar_board: **Formation** : BTS SIO 2ème année - Option SISR  
> :school: **Établissement** : Lycée Paul-Louis Courier, Tours  
> :calendar: **Date** : Septembre 2026

---

Table NAT sur le pare feu Stormshield

| **IP Src**        | **Port Src** | **IP Dst**     | **Port Dst** | **IP Src**  | **Port Src**         | **IP Dst**     | **Port Dst** |
| ----------------- | ------------ | -------------- | ------------ | ----------- | -------------------- | -------------- | ------------ |
| 192.168.3.0/24    | Any          | Any (Internet) | Any          | 172.16.32.3 | Dynamique (éphémère) | Any (Internet) | Any          |
| 172.16.53.0/24    | Any          | Any (Internet) | Any          | 172.16.32.3 | Dynamique (éphémère) | Any (Internet) | Any          |
| 192.168.33.248/29 | Any          | Any            | Any          | 172.16.32.3 | Dynamique            | Any            | Any          |
