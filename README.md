# projet_annuel_MSI2
Ce repo contient le développement de notre projet annuel, réalisé dans le cadre de notre deuxième année de master en sécurité informatique.

## AI NIDS
Le but de ce projet annuel est de créer un NIDS (Network Intrusion Detection System) basé sur l'IA (Intelligence Artificielle).
Ce projet prendra la forme d'un micro service, qui pourra être installé facilement sur une machine linux.

### Dataset
Pour l'entrainement du modèle, nous nous sommes basé sur ce dataset : [network-packet-flow-header-payload](https://huggingface.co/datasets/rdpahalavan/network-packet-flow-header-payload)

### Architecture
Pour la première version de notre projet nous le mettrons en place en suivant le schéma ci-dessous
![schema_architecture_v1](https://github.com/PierreKzh/projet_annuel_MSI2/tree/main/img/schema_architecture_v1.png)

### Dossiers
**python_scripts** : Contient les différents blocs python
**stockage** : Contient les différents systèmes de stockage
