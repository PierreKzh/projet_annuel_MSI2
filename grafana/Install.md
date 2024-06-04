# Install and configuration of grafana with AINIDS on Ubuntu(22.04)

## Install
### Install package
```bash
sudo apt-get install -y adduser libfontconfig1 musl
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_11.0.0_amd64.deb
sudo dpkg -i grafana-enterprise_11.0.0_amd64.deb
```

### Start package
```bash
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable grafana-server
sudo /bin/systemctl start grafana-server
```

## Configuration
### Connect to the web interface
```
http://<IP>:3000/login
```
[http://localhost:3000/login](http://localhost:3000/login)

### Add sqlite connection
![grafana_add_sqlite_connection](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_add_sqlite_connection.png)

### Add datasource
![grafana_add_new_datasource](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_add_new_datasource.png)  
![grafana_add_sqlite_datasource](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_add_sqlite_datasource.png)

### Configure datasource
Change the **OutputDBFile** variable in the `file.conf` to `OutputDBFile = /var/lib/grafana/db.sqlite`.  
Then initialize the db.sqlite with running the `python_scripts/Initialisation/Init.py`.  
![grafana_configure_sqlite_datasource](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_configure_sqlite_datasource.png)

### Import the dashboard
![grafana_create_dashboard](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_create_dashboard.png)  
![grafana_import_dashboard](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_import_dashboard.png)  
Select the `grafana/dashboard.json` to import.  
![grafana_choose_dashboard_to_import](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_choose_dashboard_to_import.png)  
![grafana_import_selected_dashboard](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_import_selected_dashboard.png)  
![grafana_view_dashboard](https://github.com/PierreKzh/projet_annuel_MSI2/blob/main/img/grafana/grafana_view_dashboard.png)
