create virtualenv and activate
## install wsl for windows
```shell
~$ wsl --install
``` 
enable the system in powershell
```shell
~$ Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

``` 
restart computer  
search for ubuntu app  
configure your ubuntu user / pw 

## install docker desktop using wsl2
make sure to update constraint file version in regard to your local python version

```shell
~$ pip install 'apache-airflow==2.5.2' --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.2/constraints-3.10.txt
```

## create airflow image
```shell
~$ docker compose up airflow-init
```
## Docker cmds
```shell 
# clone
docker run --name repo alpine/git clone https://github.com/docker/getting-started.git

# build
docker build -t docker101tutorial .

# run
docker run -d -p 80:80 --name docker-tutorial docker101tutorial

# save
docker tag docker101tutorial albabuhin/docker101tutorial

#share
docker push albabuhin/docker101tutorial
```

