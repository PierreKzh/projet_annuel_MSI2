# projet_annuel_MSI2
This repo contains the development of our annual project, carried out as part of our second year of a master's degree in IT security.

## AI NIDS
The goal of this annual project is to create a NIDS (Network Intrusion Detection System) based on AI (Artificial Intelligence).  
This project will take the form of a microservice, which can be easily installed on a Linux machine.

### Dataset
For training the model, we based ourselves on this dataset : [network-packet-flow-header-payload](https://huggingface.co/datasets/rdpahalavan/network-packet-flow-header-payload)

### Architecture
We decided to create the following architecture:  
![schema_architecture_v2](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/schema_architecture_v2.png)

### Folders
- **python_scripts** : Contains the different python blocks as well as the configuration file
- **models** : Contains different epochs of the model, more or less efficient
- **grafana** : Contains the procedure to follow to install grafana in addition to the system
