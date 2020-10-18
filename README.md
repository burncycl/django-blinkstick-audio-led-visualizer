
### Prerequisites
```
sudo apt install redis-server
```

### Bootstrapping Django for the first time.

Inside a blank repository
```
django-admin.py startproject bsv 
cd ./bsv
python3 manage.py startapp bsvapp
```

### Enable Virtual Environment + Development Mode
```
source ./init.sh
``` 
