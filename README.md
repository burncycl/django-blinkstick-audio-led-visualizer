
### Ansible Automated Installation (use this for Production mode install)

Want to provision a fleet of Raspberry Pi's with Django Blinkstick App transmitting via network? DevOps to the rescue.

* Reference: https://github.com/burncycl/ansible-blinkstick-audio-led-visualizer

```
make bsvapp
```

### Semi-Automated Installation

#### Prerequisites
```
sudo ./install.sh 
```

#### Enable Virtual Environment + Development Mode
```
source ./init.sh
``` 
Will start pulseaudio

#### Start Django in Development mode.

Starts Celery worker(s) and Django in Development mode
```
./boot_workers.sh
./start.sh
```

### Starting from scratch

#### Bootstrapping Django for the first time.

Inside a blank repository
```
django-admin.py startproject bsv
cd ./bsv
python3 manage.py startapp bsvapp
```
